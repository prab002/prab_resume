"""Find fresh remote jobs that hire from India, ranked against this resume.

Usage:
  python3 jobs/fetch_remote.py                      # last 7 days, default role searches
  python3 jobs/fetch_remote.py --days 2 --query "next.js" --query "founding engineer"
  python3 jobs/fetch_remote.py --include-india-only # also keep listings restricted to India

Sources are public JSON APIs that need no login: employer job boards on Ashby, Greenhouse and Lever (companies
listed in jobs/ats_boards.txt; their forms need no account, so these are the easiest to apply to), Himalayas
(filtered to jobs open to India), Remotive and RemoteOK (filtered to Worldwide, Anywhere, APAC, Asia or India).
Employer boards keep standing roles open for months, so --days does not apply to them. Writes ~/.proficiently/leads/leads-<date>.md,
skipping jobs already listed in an earlier leads file or in ~/.proficiently/job-history.md.
"""
import argparse
import html
import json
import os
import re
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
# Private job-search data lives outside this public repo (override with PROFICIENTLY_DIR).
DATA = Path(os.environ.get("PROFICIENTLY_DIR", Path.home() / ".proficiently"))
UA = {"User-Agent": "Mozilla/5.0 (job-search script for one candidate)"}

DEFAULT_QUERIES = ["full stack", "next.js", "react node", "frontend engineer", "founding engineer", "tech lead"]

# Titles worth reading. Anything matching SKIP_TITLE is dropped even if it matches here.
WANT_TITLE = re.compile(r"full[ -]?stack|front[ -]?end|react|next\.?js|node|javascript|typescript|software engineer|"
                        r"software developer|web developer|product engineer|founding engineer|tech(nical)? lead|"
                        r"lead engineer|engineering manager", re.I)
SKIP_TITLE = re.compile(r"\.net|\bjava\b|php|ruby|rails|laravel|wordpress|shopify|salesforce|ios|android|flutter|"
                        r"data scien|machine learning|ml engineer|devops|sre\b|qa\b|test|security|sales|marketing|"
                        r"support|intern\b|principal|staff|director|vp\b|head of|angular|vue|unity|game|embedded|"
                        r"blockchain|solidity|web3", re.I)
OPEN_TO_INDIA = re.compile(r"worldwide|anywhere|global|apac|asia|india|remote$|^$", re.I)
# Employer boards: a location must name India/APAC/Asia/worldwide, or be a bare "Remote" with no country.
BOARD_OPEN = re.compile(r"india|apac|asia|anywhere|worldwide|global", re.I)
BOARD_BARE_REMOTE = re.compile(r"^\s*(fully\s+)?remote\s*$|^\s*home based\s*$", re.I)
BOARDS_FILE = REPO / "jobs" / "ats_boards.txt"

# What the resume can back up, with weights. Matching is on the job description text.
STRENGTHS = {
    r"next\.?js": 3, r"\breact\b": 3, r"node\.?js|\bnode\b": 3, r"express": 1, r"postgres": 2, r"mongo": 1,
    r"redis": 1, r"kafka": 1, r"rabbitmq": 1, r"graphql": 1, r"\baws\b": 1, r"docker": 1, r"microservice": 1,
    r"\bssr\b|server[- ]side render": 1, r"tailwind": 1, r"\bgo\b|golang": 1, r"\bai\b|llm": 1, r"ci/cd": 1,
}
GAPS = {r"typescript": "TypeScript", r"\bpython\b": "Python", r"kubernetes|\bk8s\b": "Kubernetes"}

# Salary floor from preferences.md: Rs 20 LPA. Jobs listing a maximum below it are dropped; unlisted pay is kept.
FLOOR_USD = 23_000
TO_USD = {"USD": 1, "EUR": 1.08, "GBP": 1.27, "CAD": 0.73, "AUD": 0.66, "INR": 1 / 88}


def fetch_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def text(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def from_himalayas(query):
    q = urllib.parse.urlencode({"q": query, "country": "IN", "limit": 20})
    for j in fetch_json(f"https://himalayas.app/jobs/api/search?{q}").get("jobs", []):
        locs = j.get("locationRestrictions") or []
        yield {
            "title": j["title"], "company": j["companyName"].strip(), "url": j.get("applicationLink") or j["guid"],
            "posted": datetime.fromtimestamp(int(j["pubDate"]), timezone.utc),
            "location": ", ".join(locs) or "Worldwide", "india_only": locs == ["India"],
            **salary(j.get("minSalary"), j.get("maxSalary"), j.get("currency") or "USD"),
            "desc": text(j.get("description")), "source": "Himalayas",
        }


def from_remotive(query):
    q = urllib.parse.urlencode({"search": query, "limit": 50})
    for j in fetch_json(f"https://remotive.com/api/remote-jobs?{q}").get("jobs", []):
        loc = (j.get("candidate_required_location") or "").strip()
        if not any(OPEN_TO_INDIA.search(part.strip()) for part in loc.split(",")):
            continue
        yield {
            "title": j["title"], "company": j["company_name"].strip(), "url": j["url"],
            "posted": datetime.fromisoformat(j["publication_date"]).replace(tzinfo=timezone.utc),
            "location": loc or "Worldwide", "india_only": loc.lower() == "india",
            "salary": j.get("salary") or "", "max_usd": None, "desc": text(j.get("description")), "source": "Remotive",
        }


def from_remoteok():
    for j in fetch_json("https://remoteok.com/api")[1:]:
        loc = (j.get("location") or "").strip()
        if not OPEN_TO_INDIA.search(loc):
            continue
        yield {
            "title": j["position"], "company": j["company"].strip(), "url": j.get("apply_url") or j["url"],
            "posted": datetime.fromisoformat(j["date"]), "location": loc or "Worldwide",
            "india_only": loc.lower() == "india",
            **salary(j.get("salary_min"), j.get("salary_max"), "USD"),
            "desc": text(j.get("description")) + " " + " ".join(j.get("tags") or []), "source": "RemoteOK",
        }


def board_open(locations):
    """True if any listed location of an employer-board job admits someone living in India."""
    return any(BOARD_OPEN.search(loc) or BOARD_BARE_REMOTE.search(loc) for loc in locations if loc)


def from_boards():
    for line in BOARDS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if not line:
            continue
        ats, slug = line.split()
        try:
            yield from BOARD_READERS[ats](slug)
        except Exception as exc:  # one company failing should not stop the run
            print(f"warning: {ats} {slug}: {exc}")


def from_ashby(slug):
    for j in fetch_json(f"https://api.ashbyhq.com/posting-api/job-board/{slug}").get("jobs", []):
        locs = [j.get("location") or ""] + [x.get("location", "") for x in j.get("secondaryLocations") or []]
        if not j.get("isListed", True) or not board_open(locs):
            continue
        yield {
            "title": j["title"], "company": slug.title(), "url": j["jobUrl"],
            "posted": datetime.fromisoformat(j["publishedAt"]), "location": ", ".join(x for x in locs if x),
            "india_only": False, "salary": "", "max_usd": None, "desc": j.get("descriptionPlain") or "",
            "source": "Ashby", "board": True,
        }


def from_greenhouse(slug):
    for j in fetch_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true").get("jobs", []):
        # Only the job's own location: "offices" holds region groupings (e.g. "Global") that say nothing here.
        locs = [(j.get("location") or {}).get("name", "")]
        if not board_open(locs):
            continue
        yield {
            "title": j["title"], "company": j.get("company_name") or slug.title(), "url": j["absolute_url"],
            "posted": datetime.fromisoformat(j.get("first_published") or j["updated_at"]),
            "location": locs[0], "india_only": False, "salary": "", "max_usd": None,
            "desc": text(html.unescape(j.get("content") or "")), "source": "Greenhouse", "board": True,
        }


def from_lever(slug):
    for j in fetch_json(f"https://api.lever.co/v0/postings/{slug}?mode=json"):
        cats = j.get("categories") or {}
        locs = [cats.get("location", "")] + list(cats.get("allLocations") or [])
        if not board_open(locs) and j.get("country") != "IN":
            continue
        yield {
            "title": j["text"], "company": slug.title(), "url": j["hostedUrl"],
            "posted": datetime.fromtimestamp(int(j["createdAt"]) / 1000, timezone.utc),
            "location": ", ".join(dict.fromkeys(x for x in locs if x)), "india_only": False, "salary": "",
            "max_usd": None, "desc": (j.get("descriptionPlain") or "") + " " + (j.get("additionalPlain") or ""),
            "source": "Lever", "board": True,
        }


BOARD_READERS = {"ashby": from_ashby, "greenhouse": from_greenhouse, "lever": from_lever}


def salary(lo, hi, cur):
    lo, hi = int(float(lo or 0)), int(float(hi or 0))
    if not (lo or hi):
        return {"salary": "", "max_usd": None}
    k = lambda n: f"{n // 1000}k"  # noqa: E731
    text_ = f"{cur} {k(lo)}–{k(hi)}" if lo and hi else f"{cur} {k(lo or hi)}"
    rate = TO_USD.get(cur.upper())
    return {"salary": text_, "max_usd": int(max(lo, hi) * rate) if rate else None}


def score(job):
    body = f"{job['title']} {job['desc']}".lower()
    points = sum(w for pat, w in STRENGTHS.items() if re.search(pat, body))
    gaps = [name for pat, name in GAPS.items() if re.search(pat, body)]
    years = [int(y) for y in re.findall(r"(\d{1,2})\+?\s*(?:or more\s*)?years", body) if 0 < int(y) < 20]
    need = max(years) if years else None
    if need and need > 5:
        points -= 3
    return points, gaps, need


def base_version(title):
    t = title.lower()
    if "founding" in t:
        return "founding-engineer"
    if "manager" in t:
        return "associate-engineering-manager"
    if "lead" in t:
        return "tech-lead"
    if re.search(r"front[ -]?end|react|next", t) and "full" not in t:
        return "senior-frontend-engineer-nextjs"
    return "senior-full-stack-engineer-remote"


def already_seen():
    seen = set()
    files = list((DATA / "leads").glob("leads-*.md")) + [DATA / "job-history.md"]
    for f in files:
        if f.exists():
            seen |= set(re.findall(r"https?://[^\s)|]+", f.read_text(encoding="utf-8")))
    return seen


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--query", action="append", help="search term (repeatable); defaults to role searches")
    ap.add_argument("--days", type=int, default=7, help="only keep jobs posted within this many days")
    ap.add_argument("--include-india-only", action="store_true")
    ap.add_argument("--min-score", type=int, default=4)
    args = ap.parse_args()

    queries = args.query or DEFAULT_QUERIES
    jobs, errors = [], []
    for q in queries:
        for src in (from_himalayas, from_remotive):
            try:
                jobs.extend(src(q))
            except Exception as exc:  # one source failing should not stop the run
                errors.append(f"{src.__name__}({q}): {exc}")
            time.sleep(0.5)
    jobs.extend(from_boards())
    try:
        jobs.extend(from_remoteok())
    except Exception as exc:
        errors.append(f"remoteok: {exc}")

    now = datetime.now(timezone.utc)
    seen, picked, keys = already_seen(), [], set()
    for j in jobs:
        key = re.sub(r"[^a-z0-9]", "", (j["company"] + j["title"]).lower())
        if key in keys or j["url"] in seen:
            continue
        keys.add(key)
        if not j.get("board") and (now - j["posted"]).days > args.days:
            continue
        if not WANT_TITLE.search(j["title"]) or SKIP_TITLE.search(j["title"]):
            continue
        if j["india_only"] and not args.include_india_only:
            continue
        if j["max_usd"] is not None and j["max_usd"] < FLOOR_USD:
            continue
        j["score"], j["gaps"], j["years"] = score(j)
        if j["score"] >= args.min_score:
            picked.append(j)
    picked.sort(key=lambda j: (-j["score"], -j["posted"].timestamp()))

    if not picked:
        print(f"No new leads from {len(jobs)} listings. Try --days 14 or another --query.")
        for e in errors:
            print("warning:", e)
        return

    out_dir = DATA / "leads"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"leads-{now:%Y-%m-%d}.md"
    lines = [f"# Remote leads, {now:%d %b %Y}", "",
             f"Searches: {', '.join(queries)}. Posted in the last {args.days} days. "
             f"{'Includes' if args.include_india_only else 'Excludes'} India-only listings. "
             "Score counts how much of the description your resume backs up; higher is better.", "",
             "| Score | Posted | Role | Company | Open to | Salary | Watch out | Start from | Link |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for j in picked:
        watch = ", ".join(j["gaps"] + ([f"{j['years']}+ yrs"] if j["years"] and j["years"] > 3 else []))
        lines.append(f"| {j['score']} | {j['posted']:%d %b} | {j['title'].replace('|', '/')} | {j['company']} | "
                     f"{j['location'][:40]} | {j['salary']} | {watch} | {base_version(j['title'])} | "
                     f"[{j['source']}]({j['url']}) |")
    if errors:
        lines += ["", "Sources that failed this run:", ""] + [f"- {e}" for e in errors]
    if out.exists():
        # Second run on the same day: append below the first table.
        lines = ["", f"## Run at {now:%H:%M} UTC", ""] + lines[2:]
        out.write_text(out.read_text(encoding="utf-8") + "\n".join(lines) + "\n", encoding="utf-8")
    else:
        out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(picked)} new leads from {len(jobs)} listings -> {out}")
    for e in errors:
        print("warning:", e)


if __name__ == "__main__":
    main()

"""Find fresh, worldwide-remote jobs at companies outside India, ranked by keyword match with this resume.

Usage:
  python3 jobs/fetch_remote.py                    # posted in the last 6 hours, worldwide-remote only
  python3 jobs/fetch_remote.py --hours 24         # wider window
  python3 jobs/fetch_remote.py --allow-apac       # also accept roles limited to APAC / Asia / India-remote

Sources are public and need no login:
  - employer job boards on Ashby, Greenhouse and Lever (companies in jobs/ats_boards.txt). Their forms need no
    account, so /apply-job can fill them end to end. Prefer these.
  - We Work Remotely, Jobicy, Working Nomads, Himalayas, Remotive and RemoteOK.

A job is kept when it was posted inside the window, its location is worldwide (Anywhere / Worldwide / Global /
a bare "Remote"), the company does not look Indian (Pvt Ltd, INR pay, Indian HQ or offices, IST-only hours),
the title fits, listed pay is not below the floor, and enough of its tech keywords are on the real resume.

Writes ~/.proficiently/leads/leads-<date>.md (table) and leads-<date>.json (with full descriptions, for
/apply-job), skipping jobs already seen in an earlier leads file or in ~/.proficiently/job-history.md.
"""
import argparse
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).parent))
from keywords import coverage  # noqa: E402

# Private job-search data lives outside this public repo (override with PROFICIENTLY_DIR).
DATA = Path(os.environ.get("PROFICIENTLY_DIR", Path.home() / ".proficiently"))
UA = {"User-Agent": "Mozilla/5.0 (job-search script for one candidate)"}
BOARDS_FILE = REPO / "jobs" / "ats_boards.txt"

QUERIES = ["full stack", "next.js", "react", "node.js", "frontend engineer", "product engineer", "founding engineer"]
WWR_FEEDS = ["remote-full-stack-programming-jobs", "remote-front-end-programming-jobs",
             "remote-back-end-programming-jobs"]

# Titles worth reading. Anything matching SKIP_TITLE is dropped even if it matches here.
WANT_TITLE = re.compile(r"full[ -]?stack|front[ -]?end|react|next\.?js|node|javascript|typescript|software engineer|"
                        r"software developer|web developer|web engineer|product engineer|founding engineer|"
                        r"tech(nical)? lead|lead engineer|application engineer|ui engineer", re.I)
SKIP_TITLE = re.compile(r"\.net|\bjava\b|php|ruby|rails|laravel|wordpress|shopify|salesforce|\bios\b|android|"
                        r"flutter|data scien|machine learning|ml engineer|devops|\bsre\b|\bqa\b|test|security|sales|"
                        r"marketing|support|intern\b|principal|staff|director|\bvp\b|head of|angular|\bvue|unity|"
                        r"game|embedded|solidity|manager|c\+\+|golang|python|mobile|data engineer|analytics", re.I)

WORLDWIDE = re.compile(r"anywhere|worldwide|world ?wide|global|international|all countries|"
                       r"^\s*(fully\s+|100% )?remote\s*$|^\s*home based\s*$|^\s*$", re.I)
APAC = re.compile(r"\bapac\b|asia|india", re.I)
# Signs the employer itself is an Indian company (the user wants companies outside India).
INDIAN_NAME = re.compile(r"pvt\.?|private limited|\bllp\b|india\b|technolog(y|ies) solutions", re.I)
INDIAN_DESC = re.compile(r"pvt\.? ?ltd|private limited|headquartered in (india|bangalore|bengaluru|mumbai|pune|"
                         r"hyderabad|delhi|gurgaon|gurugram|noida|chennai|kolkata|ahmedabad)|"
                         r"(office|offices|based) in (bangalore|bengaluru|pune|hyderabad|noida|gurgaon|gurugram|"
                         r"chennai|mumbai|ahmedabad|indore|jaipur|kochi)|\bist (shift|hours|time ?zone)|"
                         r"\b(lpa|ctc)\b|₹", re.I)

# "Remote" titles often hide a region rule in the description. These phrases drop a job unless the description
# also says it is open worldwide.
DESC_RESTRICTED = re.compile(
    r"anywhere in (europe|the (us|u\.s\.|united states|uk|eu|americas))|(us|u\.s\.) east coast|"
    r"must (be|live|reside)\w* (based |located )?in (the )?(us|u\.s\.|usa|united states|uk|europe|eu|canada|emea|latam)|"
    r"(authori[sz]ed|eligible|legally able) to work in (the )?(us|u\.s\.|usa|united states|uk|eu|canada)|"
    r"(us|u\.s\.|usa)[- ]only|(uk|eu|emea|europe)[- ]only|central european (time|timezone)|\bcet\b|"
    r"\b(pst|est|et|pt) (hours|time ?zone)|within (the )?(us|united states|europe|emea)|"
    r"remote (within|in) (the )?(us|united states|uk|europe|eu|canada|emea|latam)", re.I)
# Only explicit statements rescue a job; company slogans like "talent, not location" sit next to region rules.
DESC_WORLDWIDE = re.compile(r"anywhere in the world|work from anywhere|from any country|any time ?zone", re.I)

# Salary floor from preferences.md: Rs 20 LPA. Jobs listing a maximum below it are dropped; unlisted pay is kept.
FLOOR_USD = 23_000
TO_USD = {"USD": 1, "EUR": 1.08, "GBP": 1.27, "CAD": 0.73, "AUD": 0.66, "INR": 1 / 88}


def fetch(url, tries=2):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8")
        except Exception:
            if attempt == tries - 1:
                raise
            time.sleep(2)


def fetch_json(url):
    return json.loads(fetch(url))


def text(s):
    s = re.sub(r"<(br|/p|/li|/h\d|/div)[^>]*>", "\n", html.unescape(s or ""))
    s = re.sub(r"<li[^>]*>", "- ", s)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    return re.sub(r"\n\s*\n+", "\n\n", re.sub(r"[ \t]+", " ", s)).strip()


def utc(dt):
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def job(**kw):
    base = {"salary": "", "max_usd": None, "board": False, "location": ""}
    return {**base, **kw}


def salary(lo, hi, cur):
    lo, hi = int(float(lo or 0)), int(float(hi or 0))
    if not (lo or hi):
        return {"salary": "", "max_usd": None}
    k = lambda n: f"{n // 1000}k"  # noqa: E731
    label = f"{cur} {k(lo)}–{k(hi)}" if lo and hi else f"{cur} {k(lo or hi)}"
    rate = TO_USD.get((cur or "").upper())
    return {"salary": label, "max_usd": int(max(lo, hi) * rate) if rate else None}


# ---- sources -------------------------------------------------------------------------------------------------

def from_boards():
    pairs = []
    for line in BOARDS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            pairs.append(line.split())

    def read(pair):
        ats, slug = pair
        try:
            return list(BOARD_READERS[ats](slug))
        except Exception as exc:  # one company failing should not stop the run
            return [{"error": f"{ats} {slug}: {exc}"}]

    with ThreadPoolExecutor(8) as ex:
        for batch in ex.map(read, pairs):
            yield from batch


def from_ashby(slug):
    for j in fetch_json(f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true").get("jobs", []):
        if not j.get("isListed", True):
            continue
        locs = [j.get("location") or ""] + [x.get("location", "") for x in j.get("secondaryLocations") or []]
        comp = (j.get("compensation") or {}).get("scrapeableCompensationSalarySummary") or ""
        yield job(title=j["title"], company=slug.replace("-", " ").title(), url=j["jobUrl"],
                  posted=utc(datetime.fromisoformat(j["publishedAt"])), location=" / ".join(x for x in locs if x),
                  salary=comp, desc=j.get("descriptionPlain") or "", source="Ashby", ats="Ashby", board=True)


def from_greenhouse(slug):
    for j in fetch_json(f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true").get("jobs", []):
        # Only the job's own location: "offices" holds region groupings (e.g. "Global") that say nothing here.
        yield job(title=j["title"], company=j.get("company_name") or slug.title(), url=j["absolute_url"],
                  posted=utc(datetime.fromisoformat(j.get("first_published") or j["updated_at"])),
                  location=(j.get("location") or {}).get("name", ""), desc=text(j.get("content")),
                  source="Greenhouse", ats="Greenhouse", board=True)


def from_lever(slug):
    for j in fetch_json(f"https://api.lever.co/v0/postings/{slug}?mode=json"):
        cats = j.get("categories") or {}
        locs = [cats.get("location", "")] + list(cats.get("allLocations") or [])
        yield job(title=j["text"], company=slug.title(), url=j["hostedUrl"],
                  posted=datetime.fromtimestamp(int(j["createdAt"]) / 1000, timezone.utc),
                  location=" / ".join(dict.fromkeys(x for x in locs if x)),
                  desc=(j.get("descriptionPlain") or "") + "\n" + (j.get("additionalPlain") or ""),
                  source="Lever", ats="Lever", board=True)


BOARD_READERS = {"ashby": from_ashby, "greenhouse": from_greenhouse, "lever": from_lever}


def from_wwr():
    for feed in WWR_FEEDS:
        root = ET.fromstring(fetch(f"https://weworkremotely.com/categories/{feed}.rss"))
        for it in root.iter("item"):
            title = it.findtext("title") or ""
            company, _, role = title.partition(":")
            yield job(title=role.strip() or title, company=company.strip(), url=it.findtext("link") or "",
                      posted=parsedate_to_datetime(it.findtext("pubDate")), location=it.findtext("region") or "",
                      desc=text(it.findtext("description")), source="WeWorkRemotely")


def from_jobicy():
    d = fetch_json("https://jobicy.com/api/v2/remote-jobs?count=100&geo=anywhere&industry=dev")
    for j in d.get("jobs", []):
        yield job(title=html.unescape(j["jobTitle"]), company=j["companyName"], url=j["url"],
                  posted=utc(datetime.fromisoformat(j["pubDate"])), location=j.get("jobGeo") or "",
                  desc=text(j.get("jobDescription")), source="Jobicy",
                  **salary(j.get("salaryMin"), j.get("salaryMax"), j.get("salaryCurrency") or "USD"))


def from_workingnomads():
    for j in fetch_json("https://www.workingnomads.com/api/exposed_jobs/"):
        if j.get("category_name") not in ("Development", "Software Development", "Engineering"):
            continue
        yield job(title=j["title"], company=j["company_name"], url=j["url"],
                  posted=utc(datetime.fromisoformat(j["pub_date"])), location=j.get("location") or "",
                  desc=text(j.get("description")) + "\n" + (j.get("tags") or ""), source="WorkingNomads")


def from_himalayas():
    for q in QUERIES:
        qs = urllib.parse.urlencode({"q": q, "country": "IN", "limit": 20})
        for j in fetch_json(f"https://himalayas.app/jobs/api/search?{qs}").get("jobs", []):
            locs = j.get("locationRestrictions") or []
            yield job(title=j["title"], company=j["companyName"].strip(), url=j.get("applicationLink") or j["guid"],
                      posted=datetime.fromtimestamp(int(j["pubDate"]), timezone.utc),
                      location=", ".join(locs) or "Worldwide", desc=text(j.get("description")), source="Himalayas",
                      **salary(j.get("minSalary"), j.get("maxSalary"), j.get("currency") or "USD"))


def from_remotive():
    for q in QUERIES:
        qs = urllib.parse.urlencode({"search": q, "limit": 50})
        for j in fetch_json(f"https://remotive.com/api/remote-jobs?{qs}").get("jobs", []):
            yield job(title=j["title"], company=j["company_name"].strip(), url=j["url"],
                      posted=utc(datetime.fromisoformat(j["publication_date"])),
                      location=j.get("candidate_required_location") or "", salary=j.get("salary") or "",
                      desc=text(j.get("description")), source="Remotive")


def from_remoteok():
    for j in fetch_json("https://remoteok.com/api")[1:]:
        yield job(title=j["position"], company=j["company"].strip(), url=j.get("apply_url") or j["url"],
                  posted=utc(datetime.fromisoformat(j["date"])), location=j.get("location") or "",
                  desc=text(j.get("description")) + "\n" + " ".join(j.get("tags") or []), source="RemoteOK",
                  **salary(j.get("salary_min"), j.get("salary_max"), "USD"))


SOURCES = [from_boards, from_wwr, from_jobicy, from_workingnomads, from_himalayas, from_remotive, from_remoteok]


# ---- filtering and ranking -----------------------------------------------------------------------------------

def location_ok(loc, allow_apac):
    parts = [p.strip() for p in re.split(r"[/;|]| or ", loc or "")] or [""]
    return any(WORLDWIDE.search(p) or (allow_apac and APAC.search(p)) for p in parts)


def indian_company(j):
    return bool(INDIAN_NAME.search(j["company"]) or INDIAN_DESC.search(j["desc"][:6000])
                or (j["salary"] or "").upper().startswith("INR"))


def candidate_corpus():
    parts = [(REPO / "resumes" / "content.py").read_text(encoding="utf-8")]
    profile = DATA / "profile.md"
    if profile.exists():
        parts.append(re.split(r"^## Open questions", profile.read_text(encoding="utf-8"), flags=re.M | re.I)[0])
    return "\n".join(parts)


def years_needed(desc):
    years = [int(y) for y in re.findall(r"(\d{1,2})\+?\s*(?:or more\s*)?years", desc.lower()) if 0 < int(y) < 20]
    return max(years) if years else None


def base_version(title):
    t = title.lower()
    if "founding" in t:
        return "founding-engineer"
    if "lead" in t:
        return "tech-lead"
    if re.search(r"front[ -]?end|react|next|\bui\b", t) and "full" not in t:
        return "senior-frontend-engineer-nextjs"
    return "senior-full-stack-engineer-remote"


def already_seen():
    seen = set()
    for f in list((DATA / "leads").glob("leads-*.md")) + [DATA / "job-history.md"]:
        if f.exists():
            seen |= set(re.findall(r"https?://[^\s)|\"]+", f.read_text(encoding="utf-8")))
    return seen


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--hours", type=float, default=6, help="only keep jobs posted within this many hours")
    ap.add_argument("--allow-apac", action="store_true", help="also accept APAC / Asia / India-remote roles")
    ap.add_argument("--min-match", type=int, default=50, help="minimum %% of the job's tech keywords he has")
    ap.add_argument("--max-years", type=int, default=6, help="skip jobs asking for more years than this")
    args = ap.parse_args()

    jobs, errors = [], []

    def run(src):
        try:
            return list(src()), None
        except Exception as exc:
            return [], f"{src.__name__}: {exc}"

    with ThreadPoolExecutor(len(SOURCES)) as ex:
        for got, err in ex.map(run, SOURCES):
            errors += [err] if err else []
            errors += [g["error"] for g in got if "error" in g]
            jobs += [g for g in got if "error" not in g]

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=args.hours)
    corpus = candidate_corpus()
    seen, keys, picked = already_seen(), set(), []
    reasons = {}

    def drop(why):
        reasons[why] = reasons.get(why, 0) + 1

    for j in jobs:
        key = re.sub(r"[^a-z0-9]", "", (j["company"] + j["title"]).lower())
        if key in keys or j["url"] in seen:
            drop("duplicate or seen before")
            continue
        keys.add(key)
        if j["posted"] < cutoff:
            drop("older than window")
            continue
        if not WANT_TITLE.search(j["title"]) or SKIP_TITLE.search(j["title"]):
            drop("title")
            continue
        if not location_ok(j["location"], args.allow_apac):
            drop("not worldwide")
            continue
        if DESC_RESTRICTED.search(j["desc"]) and not DESC_WORLDWIDE.search(j["desc"]):
            drop("region rule in description")
            continue
        if indian_company(j):
            drop("Indian company")
            continue
        if j["max_usd"] is not None and j["max_usd"] < FLOOR_USD:
            drop("pay below floor")
            continue
        need = years_needed(j["desc"])
        if need and need > args.max_years:
            drop("too many years")
            continue
        pct, have, gaps = coverage(j["title"] + "\n" + j["desc"], corpus)
        if pct < args.min_match:
            drop("low keyword match")
            continue
        j.update(match=pct, have=have, gaps=gaps, years=need, base=base_version(j["title"]))
        picked.append(j)
    picked.sort(key=lambda j: (-j["match"], -j["posted"].timestamp()))

    per_source = {}
    for j in jobs:
        per_source[j["source"]] = per_source.get(j["source"], 0) + 1
    print("Read per source: " + ", ".join(f"{k} {v}" for k, v in sorted(per_source.items())))
    summary = ", ".join(f"{k}: {v}" for k, v in sorted(reasons.items(), key=lambda kv: -kv[1]))
    print(f"{len(jobs)} listings read. Dropped -> {summary or 'none'}")
    for e in errors[:10]:
        print("warning:", e)
    if not picked:
        print(f"No new leads in the last {args.hours:g} hours. Try --hours 24 or --allow-apac.")
        return

    out_dir = DATA / "leads"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = f"{now:%Y-%m-%d}"
    md, js = out_dir / f"leads-{stamp}.md", out_dir / f"leads-{stamp}.json"
    lines = ["", f"## Run at {now:%H:%M} UTC: last {args.hours:g} hours, "
             f"{'worldwide + APAC' if args.allow_apac else 'worldwide only'}, no Indian companies", "",
             "| Match | Posted (UTC) | Role | Company | Location | Salary | Gaps | Start from | Apply via | Link |",
             "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for j in picked:
        gaps = ", ".join(j["gaps"][:5]) + (f", {j['years']}+ yrs" if j["years"] and j["years"] > 3 else "")
        lines.append(f"| {j['match']}% | {j['posted']:%d %b %H:%M} | {j['title'].replace('|', '/')} | "
                     f"{j['company']} | {j['location'][:35]} | {j['salary']} | {gaps} | {j['base']} | "
                     f"{j.get('ats') or j['source']} | [{j['source']}]({j['url']}) |")
    head = "" if md.exists() else f"# Remote leads, {now:%d %b %Y}\n"
    md.write_text((md.read_text(encoding="utf-8") if md.exists() else head) + "\n".join(lines) + "\n",
                  encoding="utf-8")
    old = json.loads(js.read_text(encoding="utf-8")) if js.exists() else []
    js.write_text(json.dumps(old + [{**j, "posted": j["posted"].isoformat()} for j in picked], indent=1,
                             ensure_ascii=False), encoding="utf-8")
    print(f"{len(picked)} new leads -> {md}")
    for j in picked[:15]:
        print(f"  {j['match']:>3}%  {j['posted']:%H:%M}  {j['company'][:22]:22} {j['title'][:55]:55} {j.get('ats') or j['source']}")


if __name__ == "__main__":
    main()

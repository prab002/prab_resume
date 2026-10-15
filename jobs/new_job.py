"""Start a job folder from a lead saved by fetch_remote.py.

Usage:
  python3 jobs/new_job.py "<lead URL>"          # or any unique part of the URL / company+title

Creates ~/.proficiently/jobs/<company-slug>-<date>/ with posting-full.txt (the description as fetched) and
meta.json (status Lead, keyword match and gaps), then prints the folder and the description for tailoring.
"""
import hashlib
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

DATA = Path(os.environ.get("PROFICIENTLY_DIR", Path.home() / ".proficiently"))


def slug(s):
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")[:40]


def from_board_url(url):
    """Read one job straight from its Ashby / Greenhouse / Lever board when it is not in a leads file."""
    sys.path.insert(0, str(Path(__file__).parent))
    import fetch_remote as fr
    from keywords import coverage
    m = re.search(r"(ashbyhq|greenhouse|lever)\.[a-z.]+/([^/?#]+)", url)
    r = re.search(r"https://([a-z0-9-]+)\.recruitee\.com/", url)
    sr = re.search(r"smartrecruiters\.com/([^/]+)/(\d+)", url)
    if m:
        ats, slug = {"ashbyhq": "ashby", "greenhouse": "greenhouse", "lever": "lever"}[m.group(1)], m.group(2)
    elif r:
        ats, slug = "recruitee", r.group(1)
    elif sr:
        ats, slug = "smartrecruiters", sr.group(1).lower()
    else:
        return None
    for j in fr.BOARD_READERS[ats](slug):
        same = (sr.group(2) in j["url"]) if sr else \
            j["url"].rstrip("/") == url.rstrip("/").removesuffix("/application")
        if same:
            pct, have, gaps = coverage(j["title"] + "\n" + j["desc"], fr.candidate_corpus())
            return {**j, "posted": j["posted"].isoformat(), "match": pct, "have": have, "gaps": gaps}
    return None


def find(needle):
    if needle.startswith("http") and (lead := from_board_url(needle)):
        return lead
    hits = {}
    for f in sorted((DATA / "leads").glob("leads-*.json")):
        for lead in json.loads(f.read_text(encoding="utf-8")):
            hay = f"{lead['url']} {lead['company']} {lead['title']}".lower()
            if needle.lower() in hay:
                hits[lead["url"]] = lead
    if len(hits) != 1:
        sys.exit(f"{len(hits)} leads match '{needle}'. Be more specific."
                 + "".join(f"\n  {h['company']} | {h['title']} | {u}" for u, h in list(hits.items())[:10]))
    return next(iter(hits.values()))


def main():
    lead = find(sys.argv[1])
    base = f"{slug(lead['company'])}-{slug(lead['title'])}".strip("-")
    folder = DATA / "jobs" / f"{base}-{date.today():%Y-%m-%d}"
    # Never reuse a folder that belongs to a different job (two roles can share a long title prefix).
    owner = folder / "meta.json"
    if owner.exists() and json.loads(owner.read_text(encoding="utf-8")).get("url") != lead["url"]:
        folder = folder.with_name(f"{folder.name}-{hashlib.sha1(lead['url'].encode()).hexdigest()[:6]}")
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "posting-full.txt").write_text(
        f"{lead['title']} at {lead['company']}\nLocation: {lead['location']}\nSalary: {lead['salary'] or 'not listed'}\n"
        f"Posted: {lead['posted']}\nURL: {lead['url']}\n\n{lead['desc']}\n", encoding="utf-8")
    meta_path = folder / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
    meta = {
        "company": lead["company"], "role": lead["title"], "url": lead["url"], "source": lead["source"],
        "ats": lead.get("ats", ""), "location": lead["location"], "salary_listed": lead["salary"] or "Not listed",
        "salary_asked": "", "fit": "", "score": lead.get("match", ""), "posted": lead["posted"],
        "keywords": ", ".join(lead.get("have", []) + lead.get("gaps", [])), "gaps": lead.get("gaps", []),
        "status": "Lead", "applied_date": "", "response_date": "", "stage": "", "notes": "",
        **{k: v for k, v in meta.items() if v not in ("", None, [])},
    }
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"FOLDER {folder}")
    print(f"MATCH {lead.get('match')}%  HAVE {', '.join(lead.get('have', []))}  GAPS {', '.join(lead.get('gaps', []))}")
    print((folder / "posting-full.txt").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

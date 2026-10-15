"""Build one resume tailored to a single job posting.

Usage:
  RESUME_PHONE="+91 ..." python3 resumes/tailor.py ~/.proficiently/jobs/<company>-<date>/tailored.json

The JSON has the same keys as a VERSIONS entry in content.py (slug, role, headline, location, summary,
skills, webknot, lead, junior, intern, achievements, keywords) plus optional "projects_first" and "base".
"base" names the closest existing version; any key left out is copied from it.

Writes resume.md and Prabhanjan-Sharma-Resume.pdf next to the JSON. Before building, it checks that every
skill listed appears somewhere in content.py or ~/.proficiently/profile.md, so a tailored resume cannot claim
a tool that is not in the real history. Pass --allow "Skill A,Skill B" only after confirming a skill is true
(and add it to profile.md so the next build accepts it without the flag).
"""
import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build  # noqa: E402
from content import VERSIONS  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent.parent / "jobs"))
from keywords import coverage  # noqa: E402

ROOT = Path(__file__).parent
REPO = ROOT.parent
# Private job-search data lives outside this public repo (override with PROFICIENTLY_DIR).
DATA = Path(os.environ.get("PROFICIENTLY_DIR", Path.home() / ".proficiently"))
REQUIRED = ["slug", "role", "headline", "location", "summary", "skills", "webknot", "lead", "junior",
            "intern", "achievements", "keywords"]


def known_text():
    """Everything the candidate has actually claimed: the shared content plus the work history profile."""
    parts = [(ROOT / "content.py").read_text(encoding="utf-8")]
    profile = DATA / "profile.md"
    if profile.exists():
        # Open questions name skills still unconfirmed, so they are not evidence.
        parts.append(re.split(r"^## Open questions", profile.read_text(encoding="utf-8"), flags=re.M | re.I)[0])
    return re.sub(r"\s+", " ", " ".join(parts)).lower()


def split_skills(value):
    # Commas inside parentheses belong to one item, e.g. "Next.js (SSR, SSG)".
    items, depth, cur = [], 0, ""
    for ch in value:
        depth += (ch == "(") - (ch == ")")
        if ch == "," and depth == 0:
            items.append(cur)
            cur = ""
        else:
            cur += ch
    items.append(cur)
    return [i.strip() for i in items if i.strip()]


def unknown_skills(v, allow):
    corpus = known_text()
    allowed = {a.strip().lower() for a in allow if a.strip()}
    missing = []
    for _, value in v["skills"]:
        for item in split_skills(value):
            core = re.sub(r"\s*\(.*?\)", "", item).strip().lower()
            if core and core not in corpus and core not in allowed:
                missing.append(item)
    return missing


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    base_slug = data.get("base")
    if base_slug:
        base = next((v for v in VERSIONS if v["slug"] == base_slug), None)
        if base is None:
            sys.exit(f"Unknown base version '{base_slug}'. Choose one of: {', '.join(v['slug'] for v in VERSIONS)}")
        data = {**base, **data}
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        sys.exit(f"tailored.json is missing: {', '.join(missing)}")
    data["skills"] = [tuple(s) for s in data["skills"]]
    return data


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("json_path")
    ap.add_argument("--allow", default="", help="comma-separated skills confirmed true but not yet in profile.md")
    args = ap.parse_args()

    src = Path(args.json_path).resolve()
    v = load(src)
    bad = unknown_skills(v, args.allow.split(","))
    if bad:
        sys.exit("These skills are not in content.py or profile.md, so they may be invented:\n  - "
                 + "\n  - ".join(bad)
                 + "\nRemove them, or confirm they are true, add them to ~/.proficiently/profile.md and rebuild.")

    out_dir = src.parent
    (out_dir / "resume.md").write_text(build.render_md(v), encoding="utf-8")
    # Recruiter-friendly file name, since upload forms show it to the hiring team.
    v = {**v, "slug": "tailored"}
    pdf, font_pt, pages = build.build_pdf(v, out_dir)
    final = out_dir / f"{build.FILE_PREFIX}-Resume.pdf"
    pdf.replace(final)
    if not build.CONTACT["phone"]:
        print("Note: RESUME_PHONE was not set, so this copy has no phone number.")
    print(f"{final}: {pages} page(s) at {font_pt}pt")
    if pages > 1:
        print("Warning: still over one page at the smallest size. Cut a bullet and rebuild.")

    # Browser upload tools can only read inside the repo, so stage a copy in the git-ignored .proficiently/.
    staged = REPO / ".proficiently" / "upload" / out_dir.name / final.name
    staged.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(final, staged)
    print(f"Upload copy: {staged}")
    keyword_report(out_dir, build.render_md(v))


def keyword_report(out_dir, resume_text):
    """Compare the job's tech keywords with the resume and with everything he can truthfully claim."""
    posting = out_dir / "posting-full.txt"
    if not posting.exists():
        print("No posting-full.txt next to the JSON, so no keyword report.")
        return
    job_text = posting.read_text(encoding="utf-8")
    pct, on_resume, _ = coverage(job_text, resume_text)
    _, true_kw, gaps = coverage(job_text, known_text())
    missing_true = sorted(set(true_kw) - set(on_resume))
    print(f"Keyword match: {pct}% of the job's tech keywords are on this resume.")
    print(f"  On resume:              {', '.join(on_resume) or '-'}")
    print(f"  True but NOT on resume: {', '.join(missing_true) or '-'}   <- add these")
    print(f"  Real gaps (never add):  {', '.join(gaps) or '-'}")


if __name__ == "__main__":
    main()

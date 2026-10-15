"""Rebuild the application tracker workbook from the per-job folders.

Usage:
  python3 jobs/tracker.py                                   # rebuild ~/.proficiently/applications.xlsx
  python3 jobs/tracker.py --set gitstart-2026-10-15 status=Interview response_date=2026-10-20

Each folder in ~/.proficiently/jobs/ holds meta.json (company, role, url, status, ...), posting-full.txt (the job
description as published), tailored.json and resume.md (what was sent) and the PDF. The workbook has:

  Applications      one row per job: dates, status, salary asked, base resume, gaps, link to the exact PDF sent
  Job descriptions  the full description of every job applied to
  Resumes sent      the full text of the resume each company received
  Insights          live response rates by base resume, source, fit and keyword, to aim future searches

Status, Response date, Stage reached and Notes typed into the workbook are kept on rebuild, so it is safe to
edit those columns by hand. Needs openpyxl.
"""
import argparse
import json
import os
import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

DATA = Path(os.environ.get("PROFICIENTLY_DIR", Path.home() / ".proficiently"))
JOBS = DATA / "jobs"
OUT = DATA / "applications.xlsx"

STATUSES = ["Lead", "Tailored", "Applied", "Screening", "Interview", "Offer", "Rejected", "No reply", "Withdrawn",
            "Skipped"]
# A status counts as a reply when the company came back in any way, including a rejection after a screen.
REPLIED = ["Screening", "Interview", "Offer"]
EDITABLE = ["status", "response_date", "stage", "notes"]

COLUMNS = [  # (key, header, width)
    ("folder", "ID", 26), ("applied_date", "Applied", 11), ("company", "Company", 20), ("role", "Role", 30),
    ("status", "Status", 11), ("response_date", "Response date", 12), ("stage", "Stage reached", 13),
    ("days", "Days to reply", 9), ("source", "Source", 11), ("ats", "ATS", 11), ("location", "Open to", 18),
    ("salary_listed", "Salary listed", 15), ("salary_asked", "Salary asked", 17), ("fit", "Fit", 7),
    ("score", "Score", 6), ("base", "Base resume", 26), ("headline", "Resume headline", 40),
    ("resume", "Resume sent", 14), ("keywords", "Job keywords", 40), ("gaps", "Gaps", 22),
    ("cover_letter", "Cover letter", 9), ("url", "Job link", 14), ("notes", "Notes", 40),
]
COL = {key: get_column_letter(i + 1) for i, (key, _, _) in enumerate(COLUMNS)}

HEAD = Font(bold=True, color="FFFFFF")
HEAD_FILL = PatternFill("solid", fgColor="13294B")
WRAP = Alignment(wrap_text=True, vertical="top")
LINK = Font(color="0563C1", underline="single")


def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else ""


def collect():
    rows = []
    for folder in sorted(JOBS.glob("*/")):
        meta_path = folder / "meta.json"
        if not meta_path.exists():
            continue
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        tailored = json.loads(read(folder / "tailored.json") or "{}")
        pdf = next(iter(sorted(folder.glob("*.pdf"))), None)
        rows.append({
            **{k: "" for k, _, _ in COLUMNS},
            **meta,
            "folder": folder.name,
            "base": tailored.get("base", meta.get("base", "")),
            "headline": tailored.get("headline", ""),
            "keywords": meta.get("keywords") or tailored.get("keywords", ""),
            "gaps": ", ".join(meta.get("gaps", [])) if isinstance(meta.get("gaps"), list) else meta.get("gaps", ""),
            "cover_letter": "Yes" if (folder / "cover-letter.md").exists() else "No",
            "resume_path": str(pdf) if pdf else "",
            "jd": read(folder / "posting-full.txt") or read(folder / "posting.md"),
            "resume_text": read(folder / "resume.md"),
        })
    return rows


def keep_manual_edits(rows, forced=None):
    """Values typed into the workbook win over meta.json for the editable columns, except fields just --set."""
    forced = forced or {}
    if not OUT.exists():
        return
    ws = load_workbook(OUT)["Applications"]
    headers = [c.value for c in ws[1]]
    idx = {key: headers.index(h) for key, h, _ in COLUMNS if h in headers}
    by_id = {r[idx["folder"]].value: r for r in ws.iter_rows(min_row=2) if r[idx["folder"]].value}
    for row in rows:
        old = by_id.get(row["folder"])
        if not old:
            continue
        for key in EDITABLE:
            if key in forced.get(row["folder"], ()):
                continue
            val = old[idx[key]].value if key in idx else None
            if val in (None, ""):
                continue
            # meta.json moved further along than the sheet (e.g. Claude logged an interview): keep meta.json.
            if key == "status" and val in STATUSES and \
                    STATUSES.index(row.get("status") or "Lead") > STATUSES.index(val):
                continue
            row[key] = val.isoformat() if hasattr(val, "isoformat") else val


def header(ws, names, widths):
    ws.append(names)
    for i, w in enumerate(widths, 1):
        cell = ws.cell(row=1, column=i)
        cell.font, cell.fill, cell.alignment = HEAD, HEAD_FILL, WRAP
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = "B2"


def to_date(s):
    try:
        return date.fromisoformat(str(s)[:10])
    except ValueError:
        return s or None


def build(rows):
    wb = Workbook()
    ws = wb.active
    ws.title = "Applications"
    header(ws, [h for _, h, _ in COLUMNS], [w for _, _, w in COLUMNS])
    for r, row in enumerate(rows, start=2):
        for c, (key, _, _) in enumerate(COLUMNS, start=1):
            cell = ws.cell(row=r, column=c)
            if key in ("applied_date", "response_date"):
                cell.value = to_date(row.get(key))
                cell.number_format = "yyyy-mm-dd"
            elif key == "days":
                a, b = COL["applied_date"], COL["response_date"]
                cell.value = f'=IF(AND(ISNUMBER({a}{r}),ISNUMBER({b}{r})),{b}{r}-{a}{r},"")'
            elif key == "resume" and row["resume_path"]:
                cell.value, cell.hyperlink, cell.font = "Open PDF", Path(row["resume_path"]).as_uri(), LINK
            elif key == "url" and row.get("url"):
                cell.value, cell.hyperlink, cell.font = "Open job", row["url"], LINK
            else:
                cell.value = row.get(key, "")
            cell.alignment = WRAP
    last = max(len(rows) + 1, 2)
    dv = DataValidation(type="list", formula1='"' + ",".join(STATUSES) + '"', allow_blank=True)
    ws.add_data_validation(dv)
    dv.add(f"{COL['status']}2:{COL['status']}500")
    ws.auto_filter.ref = f"A1:{get_column_letter(len(COLUMNS))}{last}"

    jd = wb.create_sheet("Job descriptions")
    header(jd, ["ID", "Company", "Role", "Job link", "Full job description"], [26, 20, 30, 40, 140])
    for row in rows:
        jd.append([row["folder"], row["company"], row["role"], row.get("url", ""), row["jd"][:32000]])
    for r in jd.iter_rows(min_row=2):
        for cell in r:
            cell.alignment = WRAP

    rs = wb.create_sheet("Resumes sent")
    header(rs, ["ID", "Company", "Base resume", "Headline", "Full resume text"], [26, 20, 26, 40, 140])
    for row in rows:
        rs.append([row["folder"], row["company"], row["base"], row["headline"], row["resume_text"][:32000]])
    for r in rs.iter_rows(min_row=2):
        for cell in r:
            cell.alignment = WRAP

    insights(wb, rows)
    return wb


def insights(wb, rows):
    ws = wb.create_sheet("Insights")
    ws.column_dimensions["A"].width = 36
    for col in "BCD":
        ws.column_dimensions[col].width = 14
    st = f"Applications!${COL['status']}$2:${COL['status']}$500"
    replied = "+".join(f'COUNTIFS({{rng}},{{val}},{st},"{s}")' for s in REPLIED)
    sent = "+".join(f'COUNTIFS({{rng}},{{val}},{st},"{s}")' for s in STATUSES[2:9])  # Applied .. Withdrawn

    def block(title, key, values):
        ws.append([])
        ws.append([title, "Applied", "Replies", "Reply rate"])
        for c in ws[ws.max_row]:
            c.font, c.fill = HEAD, HEAD_FILL
        rng = f"Applications!${COL[key]}$2:${COL[key]}$500"
        for v in values:
            r = ws.max_row + 1
            ws.append([v, "=" + sent.format(rng=rng, val=f"$A{r}"), "=" + replied.format(rng=rng, val=f"$A{r}"),
                       f'=IF(B{r}>0,C{r}/B{r},"")'])
            ws[f"D{r}"].number_format = "0%"

    ws.append(["Live from the Applications sheet. Set Status as companies reply; the numbers update."])
    ws["A1"].font = Font(italic=True)
    r = ws.max_row + 2
    ws.append([])
    ws.append(["Total applied", f'=COUNTA({st})-COUNTIF({st},"Lead")-COUNTIF({st},"Tailored")-COUNTIF({st},"Skipped")'])
    ws.append(["Replies", "=" + "+".join(f'COUNTIF({st},"{s}")' for s in REPLIED)])
    ws.append(["Reply rate", f"=IF(B{r}>0,B{r + 1}/B{r},\"\")"])
    ws[f"B{r + 2}"].number_format = "0%"

    block("By base resume", "base", sorted({x["base"] for x in rows if x["base"]}))
    block("By source", "source", sorted({x["source"] for x in rows if x.get("source")}))
    block("By fit", "fit", ["High", "Medium", "Low"])

    # Keyword view is computed here (not a formula): which posting keywords show up in jobs that replied.
    ws.append([])
    ws.append(["Job keyword", "In applied jobs", "In jobs that replied", "Reply rate"])
    for c in ws[ws.max_row]:
        c.font, c.fill = HEAD, HEAD_FILL
    total, hits = Counter(), Counter()
    for x in rows:
        if x.get("status") in STATUSES[2:9]:
            kws = {k.strip().lower() for k in re.split(r",", x.get("keywords") or "") if k.strip()}
            total.update(kws)
            if x.get("status") in REPLIED:
                hits.update(kws)
    for kw, n in total.most_common(40):
        ws.append([kw, n, hits[kw], hits[kw] / n if n else ""])
        ws[f"D{ws.max_row}"].number_format = "0%"


def set_fields(folder, pairs):
    meta_path = JOBS / folder / "meta.json"
    if not meta_path.exists():
        sys.exit(f"No meta.json in {JOBS / folder}")
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    for pair in pairs:
        key, _, val = pair.partition("=")
        if key == "status" and val not in STATUSES:
            sys.exit(f"Status must be one of: {', '.join(STATUSES)}")
        meta[key] = val
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--set", nargs="+", metavar=("FOLDER", "KEY=VALUE"), help="update one job's meta.json first")
    args = ap.parse_args()
    forced = {}
    if args.set:
        set_fields(args.set[0], args.set[1:])
        forced[args.set[0]] = {pair.partition("=")[0] for pair in args.set[1:]}
    rows = collect()
    keep_manual_edits(rows, forced)
    build(rows).save(OUT)
    applied = sum(1 for r in rows if r.get("status") in STATUSES[2:9])
    print(f"{OUT}: {len(rows)} jobs, {applied} applied")


if __name__ == "__main__":
    main()

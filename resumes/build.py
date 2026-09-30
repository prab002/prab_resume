"""Build one-page, ATS-friendly PDF and Markdown resumes for every version.

Usage: RESUME_PHONE="+91 ..." python3 resumes/build.py   (omit RESUME_PHONE for the public copies)
Needs Chromium (CHROME env var or the Playwright copy under /opt/pw-browsers) and pypdf.
"""
import html
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter

sys.path.insert(0, str(Path(__file__).parent))
from content import (ADRIXUS, CONTACT, EDUCATION, INV, INV_JR, INV_LEAD,  # noqa: E402
                     PROJECTS, PROJECTS_FIRST, PROJECTS_SENTENCE, VERSIONS, WEBKNOT)

ROOT = Path(__file__).parent
PDF_DIR = ROOT / "pdf"
MD_DIR = ROOT / "markdown"
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
FILE_PREFIX = "Prabhanjan-Sharma"

e = html.escape


def file_stem(v):
    return f"{FILE_PREFIX}-{v['slug']}-resume"


def bullets(items):
    return "<ul>" + "".join(f"<li>{e(b)}</li>" for b in items) + "</ul>"


def job_head(left, right):
    return f'<div class="row"><div>{left}</div><div class="date">{e(right)}</div></div>'


def summary(v):
    return f"{v['summary']} {PROJECTS_SENTENCE}"


def projects_html():
    items = []
    for p in PROJECTS:
        head = f'<b>{e(p["name"])}</b> | <a href="{p["url"]}">{e(p["label"])}</a>'
        items.append(f"<li>{head}{': ' + e(p['desc']) if p['desc'] else ''}</li>")
    return "<h2>Projects</h2><ul class=\"projects\">" + "".join(items) + "</ul>"


def render_html(v, font_pt, margin_mm):
    c = CONTACT
    contact = " | ".join(part for part in [
        f'<a href="mailto:{e(c["email"])}">{e(c["email"])}</a>',
        e(c["phone"]),
        f'<a href="{c["linkedin"]}">{e(c["linkedin_label"])}</a>',
        f'<a href="{c["github"]}">{e(c["github_label"])}</a>',
    ] if part)
    skills = "".join(f"<li><b>{e(k)}:</b> {e(val)}</li>" for k, val in v["skills"])
    body = f"""
<header>
  <h1>{e(c['name'])}</h1>
  <p class="headline">{e(v['headline'])}</p>
  <p class="meta">{e(v['location'])}</p>
  <p class="meta">{contact}</p>
</header>
<h2>Summary</h2>
<p>{e(summary(v))}</p>
{projects_html() if v['slug'] in PROJECTS_FIRST else ''}
<h2>Skills</h2>
<ul class="skills">{skills}</ul>
<h2>Experience</h2>
{job_head(f"<b>{e(WEBKNOT[0])}</b>, {e(WEBKNOT[1])} | <b>{e(WEBKNOT[2])}</b>", WEBKNOT[3])}
{bullets(v['webknot'])}
{job_head(f"<b>{e(INV[0])}</b>, {e(INV[1])}", INV[2])}
{job_head(f"<b>{e(INV_LEAD[0])}</b> (promoted)", INV_LEAD[1])}
{bullets(v['lead'])}
{job_head(f"<b>{e(INV_JR[0])}</b>", INV_JR[1])}
{bullets(v['junior'])}
{job_head(f"<b>{e(ADRIXUS[0])}</b>, {e(ADRIXUS[1])} | <b>{e(ADRIXUS[2])}</b>", ADRIXUS[3])}
{bullets(v['intern'])}
{'' if v['slug'] in PROJECTS_FIRST else projects_html()}
<h2>Education</h2>
{job_head(f"<b>{e(EDUCATION[0])}</b>, {e(EDUCATION[1])}", EDUCATION[2])}
<h2>Achievements</h2>
{bullets(v['achievements'])}
"""
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>{e(c['name'])} | {e(v['role'])} Resume</title>
<meta name="author" content="{e(c['name'])}">
<meta name="keywords" content="{e(v['keywords'])}">
<style>
  @page {{ size: A4; margin: {margin_mm}mm {margin_mm + 2}mm; }}
  * {{ box-sizing: border-box; }}
  body {{ font-family: Arial, "Liberation Sans", Helvetica, sans-serif; font-size: {font_pt}pt;
         line-height: 1.32; color: #1a1a1a; margin: 0; }}
  a {{ color: #1a1a1a; text-decoration: none; }}
  header {{ text-align: center; margin-bottom: 4pt; }}
  h1 {{ font-size: {font_pt * 2.1:.1f}pt; margin: 0; letter-spacing: 0.5pt; color: #13294b; }}
  .headline {{ font-size: {font_pt * 1.12:.1f}pt; font-weight: bold; margin: 2pt 0 1pt; color: #13294b; }}
  .meta {{ margin: 0; color: #333; }}
  h2 {{ font-size: {font_pt * 1.1:.1f}pt; text-transform: uppercase; letter-spacing: 0.8pt; color: #13294b;
        border-bottom: 1px solid #13294b; margin: 7pt 0 3pt; padding-bottom: 1pt; }}
  p {{ margin: 0 0 2pt; }}
  ul {{ margin: 1pt 0 3pt; padding-left: 13pt; }}
  li {{ margin: 0 0 1pt; }}
  ul.skills {{ list-style: none; padding-left: 0; }}
  ul.projects li {{ margin-bottom: 2pt; }}
  .row {{ display: flex; justify-content: space-between; gap: 8pt; margin-top: 3pt; }}
  .date {{ white-space: nowrap; }}
</style></head><body>{body}</body></html>"""


def print_pdf(html_text, out_pdf):
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "resume.html"
        src.write_text(html_text, encoding="utf-8")
        subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={out_pdf}", src.as_uri()],
                       check=True, capture_output=True, timeout=120)


def set_metadata(pdf_path, v):
    reader = PdfReader(pdf_path)
    writer = PdfWriter(clone_from=reader)
    writer.add_metadata({
        "/Title": f"{CONTACT['name']} | {v['role']} Resume",
        "/Author": CONTACT["name"],
        "/Subject": v["headline"],
        "/Keywords": v["keywords"] + ", " + ", ".join(p["name"] for p in PROJECTS),
        "/Creator": "resumes/build.py",
    })
    with open(pdf_path, "wb") as fh:
        writer.write(fh)


def build_pdf(v):
    out = PDF_DIR / f"{file_stem(v)}.pdf"
    # Shrink the type in small steps until the resume fits on one page.
    for font_pt, margin in [(10, 12), (9.75, 11), (9.5, 10), (9.25, 10), (9, 9)]:
        print_pdf(render_html(v, font_pt, margin), out)
        pages = len(PdfReader(out).pages)
        if pages == 1:
            break
    set_metadata(out, v)
    return out, font_pt, pages


def render_md(v):
    c = CONTACT
    lines = [
        f"# {c['name']}", "", f"**{v['headline']}**", "", v["location"], "",
        " | ".join(x for x in [c["email"], c["phone"], f"[{c['linkedin_label']}]({c['linkedin']})",
                               f"[{c['github_label']}]({c['github']})"] if x),
        "", "## Summary", "", summary(v), "",
    ]
    projects = ["## Projects", ""] + [
        f"- **{p['name']}** | [{p['label']}]({p['url']})" + (f": {p['desc']}" if p["desc"] else "") for p in PROJECTS
    ] + [""]
    if v["slug"] in PROJECTS_FIRST:
        lines += projects
    lines += ["## Skills", ""]
    lines += [f"- **{k}:** {val}" for k, val in v["skills"]]
    lines += ["", "## Experience", "", f"**{WEBKNOT[0]}**, {WEBKNOT[1]} | **{WEBKNOT[2]}** | {WEBKNOT[3]}", ""]
    lines += [f"- {b}" for b in v["webknot"]]
    lines += ["", f"**{INV[0]}**, {INV[1]} | {INV[2]}", "", f"**{INV_LEAD[0]}** (promoted) | {INV_LEAD[1]}", ""]
    lines += [f"- {b}" for b in v["lead"]]
    lines += ["", f"**{INV_JR[0]}** | {INV_JR[1]}", ""]
    lines += [f"- {b}" for b in v["junior"]]
    lines += ["", f"**{ADRIXUS[0]}**, {ADRIXUS[1]} | **{ADRIXUS[2]}** | {ADRIXUS[3]}", ""]
    lines += [f"- {b}" for b in v["intern"]]
    lines += [""]
    if v["slug"] not in PROJECTS_FIRST:
        lines += projects
    lines += ["## Education", "", f"**{EDUCATION[0]}**, {EDUCATION[1]} | {EDUCATION[2]}", "",
              "## Achievements", ""]
    lines += [f"- {b}" for b in v["achievements"]]
    return "\n".join(lines) + "\n"


def main():
    PDF_DIR.mkdir(exist_ok=True)
    MD_DIR.mkdir(exist_ok=True)
    for v in VERSIONS:
        (MD_DIR / f"{file_stem(v)}.md").write_text(render_md(v), encoding="utf-8")
        out, font_pt, pages = build_pdf(v)
        print(f"{out.relative_to(ROOT.parent)}: {pages} page(s) at {font_pt}pt")


if __name__ == "__main__":
    main()

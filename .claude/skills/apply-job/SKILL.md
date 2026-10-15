---
name: apply-job
description: Apply to one job end to end - read the posting, check fit, tailor the resume to it, build the PDF, fill the application form in Chrome, upload the resume, and submit after the user approves. Use when the user gives a job URL and wants to apply, or says "apply to the next lead".
argument-hint: "job URL, or 'next' for the top unapplied lead"
---

# Apply to a job

Adapted from the proficiently tailor-resume, cover-letter and apply skills
(https://github.com/proficientlyjobs/proficiently-claude-skills, MIT). The difference: the tailored resume
is built by this repo's PDF builder, so it is a one-page ATS-readable PDF, not Markdown, and Chrome uploads it.

## Files

- Repo (public): `resumes/content.py` (every fact), `resumes/build.py`, `resumes/tailor.py`, `jobs/fetch_remote.py`
- Private data, `DATA = ~/.proficiently/` (or `$PROFICIENTLY_DIR`). Never copy anything from here into the repo.
  - `profile.md`: work history and confirmed skills. `preferences.md`: what counts as a good job.
  - `application-data.md`: form answers. `job-history.md`: tracker. `leads/`: output of fetch_remote.py.
  - `jobs/<company-slug>-<YYYY-MM-DD>/`: one folder per application (`meta.json`, `posting-full.txt`,
    `posting.md`, `tailored.json`, `resume.md`, the PDF, optional `cover-letter.md`, `applied.md`).
  - `applications.xlsx`: tracker built by `jobs/tracker.py` from the job folders. Never edit it with code;
    rebuild it. The user edits Status / Response date / Stage reached / Notes in Excel and rebuilds keep them.
- `references/ats-patterns.md`: how Greenhouse, Lever and Workday forms behave under browser automation.

## Rules that override speed

1. **Never invent.** Only use facts from `content.py` and `profile.md`. Do not add a skill, metric, client,
   team size or title that is not written there. If the job wants something missing (TypeScript is the common
   one), leave it off and mention the gap to the user. `tailor.py` blocks unknown skills; never bypass it with
   `--allow` unless the user has just confirmed the skill and you have added it to `profile.md`.
2. **Never submit without an explicit "yes" for this specific application.** Approval for one job is not
   approval for the next.
3. **Never create accounts, solve CAPTCHAs or type passwords.** Ask the user to sign in and say "continue".
4. Do not change job titles or dates. Keep the resume to one page.

## Lessons from real applications (2026-10-15)

- **One application per company.** ElevenLabs rejects a second application in the same area within 90 days;
  other companies do the same. Check `DATA/job-history.md` for the company before tailoring.
- **Read the posting for region rules, not just the location field.** "Remote" often hides "anywhere in Europe",
  "US East Coast", "authorized to work in the US" or CET hours. Aggregator "Anywhere" labels were wrong for
  Typeform and Vercel; the employer's own board is the truth.
- **Forms that need the user are skipped**: Himalayas apply buttons (account), Recruitee forms including the
  Tether group (visible hCaptcha), Workday (account). Ashby, Greenhouse and Lever have gone through unattended.
- **Too senior**: titles like "Engineering Lead" that manage leads or report to a CTO are skipped.
- Cookie banners: choose "necessary only". Consent checkboxes: tick only the required ones.
- Phone fields often default to another country's code; set India, then type the full number and check it.
- Salary in a local currency (e.g. PLN net per month): convert the USD 40–45k/yr target and say so in notes.
- Questions about experience not in the profile (e.g. AI coding agents, using the company's product): say
  plainly it is not there yet, or leave optional ones blank. Never invent it.

## Workflow

### 1. Pick the job

- URL given: use it. `next`: open the newest file in `DATA/leads/`, take the highest-scoring row whose link is
  not already in `DATA/job-history.md`, and tell the user which one you picked.
- If a folder for this company and role already exists in `DATA/jobs/`, reuse it.

### 2. Read the posting

Fetch the page (WebFetch first; Claude in Chrome if it needs JavaScript or the user's login). Aggregator links
(Himalayas, Remotive, RemoteOK) usually link onward to the employer's ATS page; follow through to the real
application URL and use that from here on.

Save the description exactly as published (plain text, no summarising) to `posting-full.txt` in the job
folder; the tracker stores it so later we can see which kinds of postings replied. Then save
`DATA/jobs/<company-slug>-<date>/posting.md` with: URL, title, company, location rules, salary, must-haves,
nice-to-haves, keywords (tools, methods, domain words), and anything about timezone or work authorization.

### 3. Check fit (stop early if it is a bad bet)

Score against `DATA/preferences.md`. Stop and tell the user, without tailoring, if any of these are true:
it needs US/UK/EU work authorization, it is onsite or hybrid, the main stack is outside the candidate's, or
it asks for far more years than he has (close to 3). Otherwise list:
- requirement -> strongest real evidence from content.py/profile.md
- gaps (no evidence), stated plainly

Write `meta.json` in the folder: `company, role, url` (the real application URL once known), `source`
(Himalayas, Remotive, RemoteOK, LinkedIn, Wellfound, Referral, ...), `ats`, `location`, `salary_listed`,
`salary_asked` (empty until the form is filled), `fit` (High/Medium/Low), `score` (from the leads file, if any),
`keywords` (comma-separated posting keywords), `gaps` (list), `status: "Tailored"`, `applied_date: ""`,
`response_date: ""`, `stage: ""`, `notes`. If you stop at the fit check, still write it with `status: "Skipped"`
and the reason in `notes`, so the tracker learns from rejected leads too.

### 4. Tailor

Write `DATA/jobs/<folder>/tailored.json`. Start from the closest base version by setting `"base"` (one of
`associate-engineering-manager`, `sde-2-senior-software-engineer`, `tech-lead`,
`senior-full-stack-engineer-remote`, `senior-frontend-engineer-nextjs`, `founding-engineer`) and override:

- `slug`: `<company-slug>`; `role`: the posting's title
- `headline`: the posting's title wording plus 2-3 of his real stack terms the posting also uses
- `location`: use the remote line from content.py (`LOC_REMOTE`) unless the posting asks for something else
- `summary`: 2-3 short sentences, each under 20 words, pointed at this role. The builder appends the projects sentence.
- `skills`: reorder groups and items so what the posting asks for comes first. Only real skills.
- `webknot`, `lead`, `junior`, `intern`: same facts, reordered and reworded to mirror the posting's language.
  Most relevant bullet first. Keep the counts close to the base so it stays one page.
- `keywords`: posting keywords he genuinely has. `projects_first`: true for startups, AI or product roles.

Writing style (from proficiently): short sentences, plain words, one idea per sentence, action verb first,
no em dashes, no "leveraging / utilizing / spanning / demonstrating", no stacked adjectives.
Critique every line once before building.

### 5. Build the PDF

```bash
RESUME_PHONE="<phone from DATA/application-data.md>" .venv/bin/python resumes/tailor.py DATA/jobs/<folder>/tailored.json
```

(Use `python3` if `.venv` does not exist; it needs `pip install pypdf`.) If it rejects skills, remove them.
If it reports more than one page, cut the weakest bullet and rebuild. Read the PDF once to check it.

### 6. Cover letter (only if the form has a field for it, or the posting asks)

Save `DATA/jobs/<folder>/cover-letter.md`: under 200 words, 3 short paragraphs. Why this company (one real
detail from the posting), the two strongest matching proofs, and a line on remote work from IST with overlap
hours. Same facts-only rule.

### 7. Fill the form in Chrome

Load the Chrome tools in one ToolSearch call (tabs_context_mcp, tabs_create_mcp, navigate, read_page, find,
form_input, computer, file_upload, javascript_tool, get_page_text). Open a new tab. Detect the ATS from the
URL and follow `references/ats-patterns.md`.

1. Scan every field first without filling.
2. Map each field to `DATA/application-data.md` (then Custom Answers, then sensible defaults).
   Salary questions: use the matching "Expected compensation" line from application-data.md (USD range on
   USD forms, INR range on INR forms, the single number when only one is allowed, hourly for contracts).
   Never write the floor, and never quote below it. Record what you entered as `salary_asked` in meta.json.
3. Show the user ONE summary: auto-filled values, proposed answers to custom questions, and anything that needs
   them (TODO values, salary, essay questions). Wait for their answers. Save new answers to Custom Answers.
4. Fill everything. Attach the resume with `file_upload` (the tailored PDF in the job folder) and the cover
   letter if needed. If upload fails, give the user the file path to attach by hand.
5. Take a screenshot of the filled form and ask: "Submit this application to <Company>?"

### 8. Submit and log

Only after the user says yes: click Submit, confirm the success page, then:
- write `DATA/jobs/<folder>/applied.md` (date, URL, ATS, status, answers that were unusual)
- update the tracker: `.venv/bin/python jobs/tracker.py --set <folder> status=Applied applied_date=<YYYY-MM-DD> ats=<ats> salary_asked="<what was entered>"`
- add a row to `DATA/job-history.md` with status `Applied`
- tell the user what was sent, and offer the next lead (`/apply-job next`)

If they say no, run `jobs/tracker.py --set <folder> status=Tailored` instead so the work is not lost.

### Later: replies

When the user says a company replied, rejected or scheduled an interview, run
`jobs/tracker.py --set <folder> status=<Screening|Interview|Offer|Rejected> response_date=<YYYY-MM-DD> stage="<what happened>"`.
After about 21 days with no reply, mark it `No reply`.

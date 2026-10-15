---
name: find-jobs
description: Find fresh remote jobs open to candidates in India, rank them against the resume, and line them up for /apply-job. Use when the user asks for new jobs, leads, or what to apply to today.
argument-hint: "optional search terms, e.g. 'next.js founding'"
---

# Find remote jobs

1. Run the fetcher from the repo root (each argument word group becomes a `--query`):

   ```bash
   .venv/bin/python jobs/fetch_remote.py --days 3            # default role searches
   .venv/bin/python jobs/fetch_remote.py --days 7 --query "next.js" --query "founding engineer"
   ```

   It writes `~/.proficiently/leads/leads-<date>.md`, already filtered to jobs open to India/APAC/worldwide,
   skipping India-only listings and anything seen before. Use `--include-india-only` only if the user asks.

   Before choosing queries, open the Insights sheet of `~/.proficiently/applications.xlsx` (via openpyxl) once
   there are 10+ applications: lean searches toward the base resumes, sources and keywords with the best reply
   rate, and away from ones with zero replies after 5+ applications.

2. Read the leads file. For the top ~8 rows, open the link (WebFetch) and drop any that fail
   `~/.proficiently/preferences.md` dealbreakers (work authorization, onsite, wrong stack, 7+ years).
   Aggregators sometimes mislabel location; the posting text wins.

3. Add the survivors to `~/.proficiently/job-history.md` with status `Lead`, and show the user a short table:
   role, company, why it fits, the gap to know about (e.g. TypeScript), and the link.

4. Recommend which to apply to first (newest and best fit first: early applicants get far more replies) and
   offer `/apply-job <url>` or `/apply-job next`.

Other places worth a manual look that have no free API: Wellfound (startup roles, many open to India),
LinkedIn with "Remote" + "Worldwide", Arc.dev, Turing, Toptal, Lemon.io, Deel and Remote.com job boards.

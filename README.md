# Prabhanjan Sharma | Resumes

Full-stack engineer (Next.js, React, Node.js) based in Bengaluru, India, open to remote roles.
[LinkedIn](https://www.linkedin.com/in/prabhanjan-sharma-38a48a221/) | [GitHub](https://github.com/prab002)

## Resume versions

Each version is one A4 page, single column, with real selectable text so applicant tracking systems (ATS) can read it.
The PDF title, subject and keywords are set to the target role.

| Target role | PDF | Markdown | Send it for |
| --- | --- | --- | --- |
| Associate Engineering Manager | [PDF](resumes/pdf/Prabhanjan-Sharma-associate-engineering-manager-resume.pdf) | [MD](resumes/markdown/Prabhanjan-Sharma-associate-engineering-manager-resume.md) | Associate EM, Engineering Lead, people-facing Team Lead |
| Senior Software Engineer (SDE-2) | [PDF](resumes/pdf/Prabhanjan-Sharma-sde-2-senior-software-engineer-resume.pdf) | [MD](resumes/markdown/Prabhanjan-Sharma-sde-2-senior-software-engineer-resume.md) | SDE-2, Senior Software Engineer, Senior Full Stack Developer (Bengaluru) |
| Tech Lead | [PDF](resumes/pdf/Prabhanjan-Sharma-tech-lead-resume.pdf) | [MD](resumes/markdown/Prabhanjan-Sharma-tech-lead-resume.md) | Tech Lead, Lead Engineer at startups |
| Senior Full Stack Engineer (Remote) | [PDF](resumes/pdf/Prabhanjan-Sharma-senior-full-stack-engineer-remote-resume.pdf) | [MD](resumes/markdown/Prabhanjan-Sharma-senior-full-stack-engineer-remote-resume.md) | Remote full-stack roles outside India |
| Senior Frontend Engineer (Next.js) | [PDF](resumes/pdf/Prabhanjan-Sharma-senior-frontend-engineer-nextjs-resume.pdf) | [MD](resumes/markdown/Prabhanjan-Sharma-senior-frontend-engineer-nextjs-resume.md) | Senior Frontend, React and Next.js roles |
| Founding Engineer | [PDF](resumes/pdf/Prabhanjan-Sharma-founding-engineer-resume.pdf) | [MD](resumes/markdown/Prabhanjan-Sharma-founding-engineer-resume.md) | Founding or early-stage engineer roles |

## Job search

- [jobs/job-search-24h.xlsx](jobs/job-search-24h.xlsx): 51 searches on LinkedIn, Naukri, Indeed and Google Jobs, already
  filtered to the last 24 hours, each mapped to a resume version, plus an application tracker.
- [jobs/leads-2026-09-30.md](jobs/leads-2026-09-30.md): specific openings found on 30 Sep 2026.

## Editing and rebuilding

All wording lives in [resumes/content.py](resumes/content.py). Change it there, then rebuild every PDF and Markdown file:

```bash
pip install pypdf
RESUME_PHONE="+91 ..." python3 resumes/build.py   # phone is optional; set CHROME=/path/to/chrome if needed
```

The phone number is kept out of this public repo: pass it through `RESUME_PHONE` when building copies to send, and
do not commit those copies. The build shrinks the type slightly when a version would spill onto a second page.

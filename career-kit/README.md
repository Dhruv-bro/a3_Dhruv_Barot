# Career Kit — Cloud Support Associate (New Grad)

A complete, ready-to-run job-hunt system for landing a **Cloud Support
Associate / Technical Support Engineer** role in Canada or the USA.

## What's inside

| Path | What it is |
|---|---|
| [`resume/RESUME.md`](resume/RESUME.md) | ATS-optimized one-page resume, keyword-matched to real Cloud Support Associate postings, with ✏️ markers for what to personalize |
| [`resume/COVER_LETTER.md`](resume/COVER_LETTER.md) | <300-word cover letter template with a pre-send checklist |
| [`COMPANIES.md`](COMPANIES.md) | 15 researched companies hiring new grads for this role family (🇨🇦 + 🇺🇸), with locations, portals, and strategy notes |
| [`job-agent/`](job-agent/) | Python agent that scans live Greenhouse/Lever job boards daily, scores openings, tracks your pipeline in CSV, and drafts personalized recruiter cold emails (you review + send) |

## The 30-day plan

**Week 1 — Foundation**
1. Fill in every `[bracket]` in the resume and cover letter; export both as PDF.
2. Start the AWS Cloud Practitioner cert if not done (2 weeks of evenings; it's the #1 filter for these roles).
3. Do the "Multi-Tier AWS Deployment" and "Linux Break-and-Fix Lab" projects from the resume if you haven't — they're weekend-sized and free-tier.

**Weeks 2–4 — Pipeline (15 min/day)**
1. Run `python job-agent/job_agent.py` each morning.
2. Apply to the top 3–5 matches on company sites (within 72h of posting).
3. Send 2–3 personalized recruiter emails from the generated drafts.
4. Check the big non-scannable employers (AWS, Microsoft, Google, IBM, Oracle — see COMPANIES.md) twice a week manually.
5. Follow up once at day 7. Track everything in `results/jobs.csv`.

Consistent output: ~60–80 quality applications + ~40 personal recruiter
touches in 30 days — with new-grad support roles, that volume reliably
produces interviews.

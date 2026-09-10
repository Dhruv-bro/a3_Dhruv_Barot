# Job Agent — Cloud Support Associate hunt, semi-automated

An AI-assisted pipeline that **finds live entry-level cloud support jobs and
drafts personalized recruiter cold emails** — while keeping you (the human)
on the send button.

## Why not fully automated?

Because fully automated hurts you:

- **Auto-submitting applications** violates the terms of service of LinkedIn,
  Indeed, Workday, and most ATS platforms — and gets accounts banned.
- **Auto-sent bulk cold email** trips spam filters fast; once your Gmail
  address has a spam reputation, even your good emails stop landing.
- **Recruiters can smell template spam instantly.** One genuinely
  personalized line out-performs 50 identical blasts. Response rates on
  personalized cold outreach run ~5–10x higher than bulk.

So the agent automates the boring 90% (finding, filtering, tracking,
drafting) and reserves the 10% that wins interviews (the personal line, the
send decision) for you. ~15 minutes/day of your time.

## Setup

```bash
cd career-kit/job-agent
pip install -r requirements.txt
python job_agent.py
```

## What you get

| Output | What it is |
|---|---|
| `results/jobs.csv` | Every matching opening, scored and sorted, with tracking columns (`status`, `applied_date`, `contact`, `follow_up`) — this is your pipeline tracker. Open it in Excel/Sheets. |
| `outbox/*.md` | One tailored cold-email draft per top match, with subject line, your profile woven in, and a clearly-marked `[⚠️ ...]` slot for the one company-specific sentence you must write. |

## Daily workflow (~15 min)

1. `python job_agent.py` — fresh scan every morning (new postings score best when applied to within 72h).
2. Open `results/jobs.csv`, pick the top 3–5 new roles, **apply on the company site first**.
3. Find the recruiter on LinkedIn (search: `"<company>" recruiter "early career"` or `"university recruiting"`).
4. Open the matching draft in `outbox/`, fill in the recruiter's name and the ⚠️ company-specific line, attach your resume PDF, send.
5. Update the CSV: `status=applied`, `contact=<recruiter>`, `follow_up=<today+7d>`.
6. Day 7 with no reply → one short, polite follow-up. Then move on.

## Using Claude as the agent driver

In a Claude Code session with the Gmail connector attached, you can say:

> "Run the job agent, then create Gmail **drafts** (don't send) for the top 5
> outbox emails, and remind me tomorrow at 9am to review them."

Claude can run the scan, create the drafts in your Gmail Drafts folder, and
schedule the reminder — you still press send. You can also ask Claude to set
up a recurring daily run.

## Tuning

Everything lives in `config.yaml`:

- **`candidate:`** — fill in your real details once; every draft uses them.
- **`search:`** — add/remove title keywords and target cities.
- **`boards:`** — company tokens for the public Greenhouse/Lever APIs. Find a
  company's token by checking whether `https://boards-api.greenhouse.io/v1/boards/<name>/jobs`
  or `https://api.lever.co/v0/postings/<name>?mode=json` returns JSON. Dead
  tokens are skipped harmlessly.

Note: AWS, Microsoft, Google, IBM, Oracle and most banks use their own ATS
(Workday etc.) with no public feed — check those (list in `../COMPANIES.md`)
manually twice a week; they're worth it.

# Agent Runbook — Daily Cloud Support Job Scan (Claude-driven)

This is the operating procedure a Claude agent session follows on each
scheduled run. It exists because the local `job_agent.py` script needs
direct internet access; in restricted environments the agent uses the
Apify actor `bovi/greenhouse-lever-ashby-job-scraper` instead (same data,
server-side filtering, per-job dataset items).

## Each run

1. **Scan** — call the actor in small shards (free tier caps ~10 items/run):
   - Shard A: `datadog`, titleKeyword `technical support engineer`
   - Shard B: `cloudflare`, `mongodb`, `gitlab`, titleKeyword `support`
   - Shard C: `twilio`, `pagerduty`, `fastly`, `okta`, `elastic`, titleKeyword `support`
   - Input per shard: `{"companies": [{"ats": "greenhouse", "company": "<slug>"}...],
     "titleKeyword": "...", "includeDescriptions": false, "outputProfile": "minimal",
     "onlyNewSinceLastRun": true}`
   - `onlyNewSinceLastRun` gives change detection — after the first snapshot,
     runs emit only NEW and CLOSED postings.

2. **Filter** — keep a job only if ALL of:
   - Title family: cloud support / technical support engineer / support
     engineer / technical solutions / technical services / support
     associate-specialist-analyst
   - NOT senior/staff/principal/lead/manager/director/head, NOT level ≥ 2
     (II, 2, 3), NOT intern
   - Location: Canada, USA, or Remote-Americas
   - No hard language requirement the candidate lacks

3. **Deliver** — for each new match:
   - Create a **Gmail draft** (never send) using the cold-email template in
     `job_agent.py` `draft_email()`, filled with the candidate profile from
     `config.yaml`, leaving the recipient blank and the one
     company-specific line marked `[⚠️ ...]` for the human to complete.
   - Report new matches + closed postings in the session summary.

4. **Remind** — the majors are not board-scannable and get many of the
   entry-level cohorts: AWS, Microsoft, Google, IBM, Oracle, Salesforce,
   ServiceNow, Rackspace, Shopify, OpenText, CGI (see `../COMPANIES.md`).
   Twice a week, remind the user to check those portals manually.

## Hard rules

- **Never send email.** Draft only; the human reviews, personalizes, sends.
- **Never auto-submit applications.** The agent surfaces links; the human applies.
- Do not add recipients to drafts unless the user supplied the address.

## Board-slug status (verified 2026-09-10)

Working Greenhouse slugs: `cloudflare`, `datadog`, `mongodb`, `gitlab`,
`elastic`, `twilio`, `pagerduty`, `fastly`, `okta`.
Dead/moved (do not use, find their new ATS before re-adding): `digitalocean`,
`hashicorp` (Greenhouse), `shopify`, `netlify`, `grafana` (Lever).

## Scan log

| Date | New matches | Notes |
|---|---|---|
| 2026-09-10 | Cloudflare — Technical Support Engineer, Application Performance (Hybrid, posted 2026-09-04) | First full scan, 35 support-titled postings reviewed; all others were level 2+, manager+, or outside US/Canada. Gmail draft created. |

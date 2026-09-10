#!/usr/bin/env python3
"""Job-hunt agent: finds live Cloud Support / Technical Support openings and
drafts personalized cold emails to recruiters.

What it does:
  1. Scans the public Greenhouse and Lever job-board APIs for the companies
     listed in config.yaml (no API keys or scraping needed — these are the
     same JSON feeds the companies' own careers pages use).
  2. Filters for entry-level cloud/technical support titles in your target
     locations, scores each match, and writes everything to results/jobs.csv.
  3. Generates a tailored cold-email draft (subject + body, markdown) for the
     top matches into outbox/, ready for you to review, personalize the one
     "[why this company]" line, and send.

What it deliberately does NOT do: send email or submit applications. You
review every draft before it leaves your machine — that keeps you out of
spam filters, out of job-board ToS trouble, and keeps quality high.

Usage:
  pip install -r requirements.txt
  python job_agent.py                 # scan + draft emails
  python job_agent.py --no-emails     # scan only
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import pathlib
import re
import sys

import requests
import yaml

HERE = pathlib.Path(__file__).resolve().parent
TIMEOUT = 20
HEADERS = {"User-Agent": "job-agent/1.0 (personal job search tool)"}


def load_config() -> dict:
    with open(HERE / "config.yaml", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def fetch_greenhouse(token: str) -> list[dict]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    if resp.status_code != 200:
        print(f"  [skip] greenhouse:{token} -> HTTP {resp.status_code}")
        return []
    jobs = resp.json().get("jobs", [])
    return [
        {
            "company": token,
            "source": "greenhouse",
            "title": j.get("title", ""),
            "location": (j.get("location") or {}).get("name", ""),
            "url": j.get("absolute_url", ""),
            "posted": (j.get("updated_at") or "")[:10],
        }
        for j in jobs
    ]


def fetch_lever(token: str) -> list[dict]:
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    if resp.status_code != 200:
        print(f"  [skip] lever:{token} -> HTTP {resp.status_code}")
        return []
    data = resp.json()
    if not isinstance(data, list):
        return []
    return [
        {
            "company": token,
            "source": "lever",
            "title": j.get("text", ""),
            "location": (j.get("categories") or {}).get("location", "") or "",
            "url": j.get("hostedUrl", ""),
            "posted": dt.datetime.fromtimestamp(
                (j.get("createdAt") or 0) / 1000
            ).strftime("%Y-%m-%d")
            if j.get("createdAt")
            else "",
        }
        for j in data
    ]


def score_job(job: dict, search: dict) -> int:
    """Return match score; <= 0 means filtered out."""
    title = f" {job['title'].lower()} "
    location = job["location"].lower()

    if any(bad in title for bad in search["exclude_keywords"]):
        return 0
    if not any(kw in title for kw in search["title_keywords"]):
        return 0

    score = 10
    score += 5 * sum(1 for s in search["entry_level_signals"] if s in title)
    if "cloud" in title:
        score += 5

    locations = search.get("locations") or []
    if locations:
        if not any(loc in location for loc in locations):
            return 0
        if "canada" in location or "remote" in location:
            score += 3
    return score


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60]


def draft_email(job: dict, cand: dict) -> str:
    company = job["company"].replace("-", " ").title()
    subject = (
        f"New grad interested in {job['title']} — "
        f"{cand['name']} (AWS + Linux, available now)"
    )
    body = f"""Subject: {subject}

Hi [Recruiter/Hiring Manager first name],

I'm {cand['name']}, a {cand['headline']}. I just applied for the
**{job['title']}** role at {company} ({job['url']}) and wanted to reach out
directly because this is exactly the kind of work I'm looking for.

Two quick reasons I think I'd do well in your support org:

1. **I troubleshoot like it's the job — because it is.** {cand['proof_point']}.
2. **I like the human half of support.** Explaining a fix clearly to a
   stressed customer matters as much as finding it, and that's the part I'm
   best at.

[⚠️ ADD ONE SPECIFIC SENTENCE ABOUT {company.upper()} — a product you've
used, a docs page or blog post you learned from, their status-page culture.
This line is the difference between a reply and the trash folder.]

Would you be open to a quick 15-minute chat, or could you point me to the
right person for early-career support hiring? My resume is attached.

Thank you either way for the work you do — I know these inboxes are busy.

Best regards,
{cand['name']}
{cand['email']} • {cand['phone']}
{cand['linkedin']} • {cand['github']}
{cand['location']}
"""
    return body


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-emails", action="store_true", help="scan only")
    args = parser.parse_args()

    cfg = load_config()
    search = cfg["search"]
    boards = cfg.get("boards", {})

    print("Scanning job boards...")
    all_jobs: list[dict] = []
    for token in boards.get("greenhouse", []):
        try:
            all_jobs += fetch_greenhouse(token)
        except requests.RequestException as exc:
            print(f"  [skip] greenhouse:{token} -> {exc}")
    for token in boards.get("lever", []):
        try:
            all_jobs += fetch_lever(token)
        except requests.RequestException as exc:
            print(f"  [skip] lever:{token} -> {exc}")

    print(f"Fetched {len(all_jobs)} total postings; filtering...")
    matches = []
    for job in all_jobs:
        s = score_job(job, search)
        if s > 0:
            job["score"] = s
            matches.append(job)
    matches.sort(key=lambda j: j["score"], reverse=True)

    csv_path = HERE / cfg["output"]["csv"]
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "score", "company", "title", "location", "posted", "url",
                "source", "status", "applied_date", "contact", "follow_up",
            ],
        )
        writer.writeheader()
        for job in matches:
            writer.writerow(
                {**job, "status": "new", "applied_date": "", "contact": "",
                 "follow_up": ""}
            )
    print(f"Wrote {len(matches)} matches -> {csv_path}")

    if not args.no_emails and matches:
        outbox = HERE / cfg["output"]["outbox"]
        outbox.mkdir(parents=True, exist_ok=True)
        top = matches[: cfg["output"].get("max_emails", 20)]
        for job in top:
            name = f"{slugify(job['company'])}--{slugify(job['title'])}.md"
            (outbox / name).write_text(
                draft_email(job, cfg["candidate"]), encoding="utf-8"
            )
        print(f"Drafted {len(top)} cold emails -> {outbox}/")
        print("Review each draft, fill the [⚠️ ...] line, then send manually")
        print("or ask Claude to create Gmail drafts from the outbox for you.")

    if not matches:
        print("No matches today — widen keywords/locations in config.yaml "
              "or add more board tokens, and run again tomorrow.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

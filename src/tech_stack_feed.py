import json
import os
import re
import time
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
OUT_FILE = DATA_DIR / "live_feed_snapshot.json"

TECH_ALIASES: dict[str, list[str]] = {
    "Python": [r"\bpython\b"],
    "TypeScript": [r"\btypescript\b", r"\bts\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
    "SQL": [r"\bsql\b"],
    "PostgreSQL": [r"\bpostgres(?:ql)?\b"],
    "Go": [r"\bgolang\b", r"\bgo\b"],
    "Rust": [r"\brust\b"],
    "Java": [r"\bjava\b"],
    "C#": [r"\bc#\.?\b", r"\b\.net\b", r"\bdotnet\b"],
    "Docker": [r"\bdocker\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "React": [r"\breact(?:\.js)?\b"],
    "Node.js": [r"\bnode(?:\.?js)?\b"],
    "AWS": [r"\baws\b", r"\bamazon web services\b"],
}

COMPILED_TECHS = {
    tech: [re.compile(pat, re.IGNORECASE) for pat in patterns]
    for tech, patterns in TECH_ALIASES.items()
}


def get_with_retry(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    max_attempts: int = 4,
) -> requests.Response:
    delay = 2.0
    for attempt in range(1, max_attempts + 1):
        resp = requests.get(url, params=params, headers=headers, timeout=20)
        if resp.status_code not in (429, 500, 502, 503, 504):
            resp.raise_for_status()
            return resp
        if attempt == max_attempts:
            resp.raise_for_status()
        print(f"Server returned {resp.status_code} (attempt {attempt}/{max_attempts}). Retrying in {delay:.1f}s...")
        time.sleep(delay)
        delay *= 2
    raise RuntimeError("Unreachable retry loop")


def extract_techs(text: str) -> list[str]:
    if not text:
        return []
    return [
        tech
        for tech, patterns in COMPILED_TECHS.items()
        if any(p.search(text) for p in patterns)
    ]


def fetch_jobs(country: str = "gb", pages: int = 2) -> tuple[int, Counter, list[dict]]:
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")
    if not app_id or not app_key:
        raise RuntimeError("Missing ADZUNA_APP_ID or ADZUNA_APP_KEY in environment.")

    seen_keys: set[tuple[str, str]] = set()
    tech_counts: Counter = Counter()
    roles: list[dict] = []
    total_unique = 0

    for page in range(1, pages + 1):
        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
        params = {
            "app_id": app_id,
            "app_key": app_key,
            "what": "software engineer developer",
            "results_per_page": 50,
            "content-type": "application/json",
        }
        resp = get_with_retry(url, params=params)
        items = resp.json().get("results", [])

        for job in items:
            company = (job.get("company", {}).get("display_name") or "Unknown").strip()
            title = (job.get("title") or "Untitled Role").strip()
            dedup_key = (company.lower(), title.lower())
            if dedup_key in seen_keys:
                continue
            seen_keys.add(dedup_key)
            total_unique += 1

            desc = job.get("description") or ""
            matched = extract_techs(f"{title} {desc}")
            for tech in matched:
                tech_counts[tech] += 1

            roles.append({
                "id": str(job.get("id", total_unique)),
                "title": title,
                "company": company,
                "location": (job.get("location", {}).get("display_name") or country.upper()),
                "created": job.get("created", ""),
                "redirect_url": job.get("redirect_url", ""),
                "tech_stack": matched,
            })

    return total_unique, tech_counts, roles


def fetch_github_momentum(days_back: int = 14) -> list[dict]:
    headers = {"Accept": "application/vnd.github+json"}
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    since_date = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime("%Y-%m-%d")
    languages = ["Python", "TypeScript", "JavaScript", "Go", "Rust", "Java", "C#"]
    momentum = []

    for lang in languages:
        q = f'language:"{lang}" pushed:>={since_date} archived:false'
        resp = get_with_retry(
            "https://api.github.com/search/repositories",
            params={"q": q, "per_page": 1},
            headers=headers,
        )
        momentum.append({
            "language": lang,
            "active_repos_14d": resp.json().get("total_count", 0),
        })

    momentum.sort(key=lambda x: x["active_repos_14d"], reverse=True)
    return momentum


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    country = os.getenv("ADZUNA_COUNTRY", "gb")

    total_jobs = 0
    job_counts: Counter = Counter()
    roles: list[dict] = []
    job_status = "ok"

    try:
        total_jobs, job_counts, roles = fetch_jobs(country=country, pages=2)
    except requests.HTTPError as exc:
        job_status = f"error: {exc}"
        print(f"Warning: Adzuna fetch failed ({exc}). Continuing with GitHub data...")

    gh_momentum = fetch_github_momentum(days_back=14)

    hiring_share = [
        {
            "tech": tech,
            "job_count": count,
            "share_pct": round((count / total_jobs * 100), 1) if total_jobs else 0.0,
        }
        for tech, count in job_counts.most_common()
    ]

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "country": country,
        "adzuna_status": job_status,
        "unique_jobs_analyzed": total_jobs,
        "hiring_demand": hiring_share,
        "github_momentum": gh_momentum,
        "roles": roles[:40],
    }

    OUT_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Saved snapshot to {OUT_FILE} (Adzuna: {job_status}, Jobs: {total_jobs}, GitHub langs: {len(gh_momentum)})")


if __name__ == "__main__":
    main()
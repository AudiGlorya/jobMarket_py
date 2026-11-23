import requests
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

HEADERS = {
    "User-Agent": "KenyaTechJobIntelligence/1.0 (Educational Research Project)"
}

# Real tech companies hiring in Kenya / East Africa on keyless ATS boards (Greenhouse / Lever / Ashby)
KENYA_TECH_BOARDS = [
    ("greenhouse", "andela", "Andela"),
    ("greenhouse", "tala", "Tala"),
    ("greenhouse", "wave", "Wave Mobile Money"),
    ("greenhouse", "flutterwave", "Flutterwave"),
    ("lever", "paystack", "Paystack"),
    ("ashby", "chippercash", "Chipper Cash"),
    ("greenhouse", "mkopa", "M-KOPA"),
    ("greenhouse", "wasoko", "Wasoko"),
    ("greenhouse", "sun-king", "Sun King"),
]

TECH_SKILLS = [
    "python", "sql", "aws", "react", "node", "java", "typescript",
    "docker", "kubernetes", "django", "flask", "azure", "gcp", "go", "php"
]

def extract_skills(text):
    text_lower = str(text).lower()
    return [skill.upper() for skill in TECH_SKILLS if skill in text_lower]

def fetch_remotive(query):
    jobs = []
    try:
        url = f"https://remotive.com/api/remote-jobs?search={requests.utils.quote(query)}&limit=30"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            for item in res.json().get("jobs", []):
                title = item.get("title", "")
                desc = item.get("description", "")
                loc = item.get("candidate_required_location", "Worldwide")
                is_kenya = any(k in loc.lower() for k in ["kenya", "africa", "emea", "worldwide", "anywhere"])
                if is_kenya:
                    jobs.append({
                        "job_title": title,
                        "company": item.get("company_name", "Unknown"),
                        "location": loc,
                        "job_scope": "International - Remote",
                        "source": "Remotive",
                        "date_posted": item.get("publication_date", "")[:10],
                        "apply_url": item.get("url", "#"),
                        "skills": extract_skills(f"{title} {desc}")
                    })
    except Exception:
        pass
    return jobs

def fetch_remoteok(query):
    jobs = []
    try:
        url = "https://remoteok.com/api"
        res = requests.get(url, headers=HEADERS, timeout=10)
        if res.status_code == 200:
            data = res.json()[1:]  # First item is legal metadata
            q_terms = query.lower().split()
            for item in data:
                title = item.get("position", "")
                tags = " ".join(item.get("tags", []))
                combined = f"{title} {tags}".lower()
                if all(term in combined for term in q_terms):
                    jobs.append({
                        "job_title": title,
                        "company": item.get("company", "Unknown"),
                        "location": item.get("location") or "Remote",
                        "job_scope": "International - Remote",
                        "source": "RemoteOK",
                        "date_posted": item.get("date", "")[:10],
                        "apply_url": item.get("url", "#"),
                        "skills": extract_skills(f"{title} {tags}")
                    })
                if len(jobs) >= 25:
                    break
    except Exception:
        pass
    return jobs

def fetch_ats_board(board_info, query):
    ats, slug, company_name = board_info
    jobs = []
    q_terms = query.lower().split()
    try:
        if ats == "greenhouse":
            url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
            res = requests.get(url, headers=HEADERS, timeout=8)
            if res.status_code == 200:
                for j in res.json().get("jobs", []):
                    title = j.get("title", "")
                    loc = (j.get("location") or {}).get("name", "Remote")
                    content = j.get("content", "")
                    if all(t in title.lower() for t in q_terms):
                        scope = "Kenya (Local)" if any(k in loc.lower() for k in ["kenya", "nairobi", "mombasa"]) else "International - Remote"
                        jobs.append({
                            "job_title": title,
                            "company": company_name,
                            "location": loc,
                            "job_scope": scope,
                            "source": "Company Careers (Greenhouse)",
                            "date_posted": (j.get("updated_at") or "")[:10],
                            "apply_url": j.get("absolute_url", "#"),
                            "skills": extract_skills(f"{title} {content}")
                        })
        elif ats == "lever":
            url = f"https://api.lever.co/v0/postings/{slug}?mode=json"
            res = requests.get(url, headers=HEADERS, timeout=8)
            if res.status_code == 200:
                for j in res.json():
                    title = j.get("text", "")
                    loc = (j.get("categories") or {}).get("location", "Remote")
                    desc = j.get("descriptionPlain", "")
                    if all(t in title.lower() for t in q_terms):
                        scope = "Kenya (Local)" if any(k in loc.lower() for k in ["kenya", "nairobi"]) else "International - Remote"
                        jobs.append({
                            "job_title": title,
                            "company": company_name,
                            "location": loc,
                            "job_scope": scope,
                            "source": "Company Careers (Lever)",
                            "date_posted": datetime.now().strftime("%Y-%m-%d"),
                            "apply_url": j.get("hostedUrl", "#"),
                            "skills": extract_skills(f"{title} {desc}")
                        })
    except Exception:
        pass
    return jobs

def search_live_jobs(role_query="software engineer"):
    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(fetch_remotive, role_query),
            executor.submit(fetch_remoteok, role_query),
        ]
        for board in KENYA_TECH_BOARDS:
            futures.append(executor.submit(fetch_ats_board, board, role_query))
            
        for f in futures:
            results.extend(f.result())
            
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.drop_duplicates(subset=["job_title", "company"])
    return df
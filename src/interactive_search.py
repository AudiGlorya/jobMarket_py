import sqlite3
import requests
import os

def get_role_intelligence(search_role):
    """Queries the historical SQLite database for role intelligence."""
    db_path = os.path.join("data", "job_market.db")
    if not os.path.exists(db_path):
        print("\n[Error] Database not found. Please run the load_to_sqlite.py script first.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Use parameterized queries with LIKE to find related roles (e.g., 'Python' matches 'Junior Python Developer')
    query = """
        SELECT 
            COUNT(*) as job_count,
            SUM(req_python) as python_reqs,
            SUM(req_sql) as sql_reqs,
            SUM(req_javascript) as js_reqs,
            SUM(req_cloud) as cloud_reqs,
            SUM(is_entry_level) as entry_level_roles
        FROM job_postings
        WHERE job_title LIKE ?
    """
    cursor.execute(query, (f'%{search_role}%',))
    results = cursor.fetchone()
    conn.close()

    job_count = results[0]
    
    print("\n" + "="*50)
    print(f"🕵️  ROLE INTELLIGENCE: {search_role.upper()}")
    print("="*50)
    
    if job_count == 0:
        print(f"No historical data found in our dataset for '{search_role}'.")
    else:
        print(f"Historical Sample Size: {job_count} advertisements analyzed.")
        print(f"- Entry-Level/Junior Positions: {results[5]}")
        print("\nTop Technical Requirements (Observed):")
        if results[1]: print(f"- Python: Required in {results[1]} postings")
        if results[2]: print(f"- SQL: Required in {results[2]} postings")
        if results[3]: print(f"- JavaScript: Required in {results[3]} postings")
        if results[4]: print(f"- Cloud (AWS/Azure/GCP): Required in {results[4]} postings")
    print("="*50)

def find_live_opportunities(search_role):
    """Fetches live job data from the permitted Remotive public API."""
    print("\n[System] Connecting to live job feeds (Remotive API)...")
    
    url = f"https://remotive.com/api/remote-jobs?search={search_role}&limit=3"
    
    try:
        response = requests.get(url)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()
        
        jobs = data.get('jobs', [])
        
        print(f"\n🌍 LIVE OPPORTUNITIES FOUND: {len(jobs)}")
        print("-" * 50)
        
        if not jobs:
            print("No active vacancies found for this role right now.")
            return

        for idx, job in enumerate(jobs[:3], 1): # Display up to 3 jobs
            print(f"{idx}. {job['title']}")
            print(f"   Employer: {job['company_name']}")
            print(f"   Type: {job['job_type'].capitalize()} | Location: {job['candidate_required_location']}")
            print(f"   Apply: {job['url']}")
            print("-" * 50)
            
    except requests.exceptions.RequestException as e:
        print(f"[Error] Could not fetch live jobs: {e}")

def main():
    while True:
        print("\n" + "*"*60)
        print("KENYA TECH JOB MARKET - INTERACTIVE DISCOVERY MODULE")
        print("*"*60)
        
        user_input = input("\nEnter a technology job role to research (e.g., 'Data', 'Developer', 'Python') or type 'exit' to quit: ").strip()
        
        if user_input.lower() == 'exit':
            print("Exiting module. Goodbye!")
            break
            
        if not user_input:
            continue
            
        # 1. Fetch Historical Intelligence
        get_role_intelligence(user_input)
        
        # 2. Ask for Live Search
        live_search = input("\nWould you like to search for matching LIVE online vacancies? (y/n): ").strip().lower()
        if live_search == 'y':
            find_live_opportunities(user_input)

if __name__ == "__main__":
    main()
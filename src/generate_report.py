import sqlite3
import pandas as pd
import os

def generate_terminal_dashboard():
    print("=" * 60)
    print("📊 KENYA TECH JOB MARKET - TERMINAL EXECUTIVE DASHBOARD")
    print("=" * 60)
    
    db_path = os.path.join("data", "job_market.db")
    if not os.path.exists(db_path):
        print("[Error] Database not found. Please run load_to_sqlite.py first.")
        return
        
    # Connect to database and read data
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM job_postings", conn)
    conn.close()
    
    total_jobs = len(df)
    entry_count = int(df['is_entry_level'].sum())
    entry_share = (entry_count / total_jobs) * 100 if total_jobs > 0 else 0
    
    # 1. Market Overview
    print(f"\n📌 1. MARKET OVERVIEW")
    print(f"   • Total Captured Job Advertisements : {total_jobs}")
    print(f"   • Unique Employers Represented      : {df['company'].nunique()}")
    print(f"   • Entry-Level / Internship Share    : {entry_count} postings ({entry_share:.1f}%)")
    
    # 2. Technical Skills Demand
    print(f"\n📌 2. TOP TECHNICAL SKILLS DEMAND")
    print(f"   • Python     : Required in {int(df['req_python'].sum())} posting(s)")
    print(f"   • SQL        : Required in {int(df['req_sql'].sum())} posting(s)")
    print(f"   • JavaScript : Required in {int(df['req_javascript'].sum())} posting(s)")
    print(f"   • Cloud Tech : Required in {int(df['req_cloud'].sum())} posting(s)")
    
    # 3. Experience Level Breakdown
    print(f"\n📌 3. EXPERIENCE LEVEL DISTRIBUTION")
    exp_counts = df['experience_level'].value_counts()
    for level, count in exp_counts.items():
        print(f"   • {level:<12} : {count} posting(s)")
        
    # 4. Geographical Distribution
    print(f"\n📌 4. GEOGRAPHICAL DISTRIBUTION")
    loc_counts = df['location'].value_counts()
    for loc, count in loc_counts.items():
        print(f"   • {loc:<12} : {count} posting(s)")

    print("\n" + "=" * 60)
    print("✅ Executive summary generated successfully from SQLite database.")
    print("=" * 60)

if __name__ == "__main__":
    generate_terminal_dashboard()
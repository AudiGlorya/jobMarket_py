import pandas as pd
import sqlite3
import os

def load_data():
    input_path = os.path.join("data", "processed", "engineered_jobs.csv")
    db_path = os.path.join("data", "job_market.db")

    print("Loading data into SQLite database...")
    
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: Could not find {input_path}. Run feature_engineering.py first.")
        return

    # Connect to SQLite and save
    with sqlite3.connect(db_path) as conn:
        df.to_sql('job_postings', conn, if_exists='replace', index=False)
        
    print(f"Database load complete! Saved {len(df)} rows to table 'job_postings' in {db_path}")

if __name__ == "__main__":
    load_data()
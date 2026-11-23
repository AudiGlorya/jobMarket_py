import pandas as pd
import os

def clean_data():
    input_path = os.path.join("data", "raw", "raw_kenya_tech_jobs.csv")
    output_dir = os.path.join("data", "interim")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "cleaned_jobs.csv")

    print("Starting data cleaning...")
    
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: Could not find {input_path}. Run data_collection.py first.")
        return

    # Drop rows without a job title
    df = df.dropna(subset=['job_title'])
    
    # Fill missing values for non-critical columns
    df['company'] = df['company'].fillna('Confidential')
    df['location'] = df['location'].fillna('Unknown')
    
    # Standardize text formatting
    df['job_title'] = df['job_title'].str.strip()
    df['company'] = df['company'].str.strip()
    
    df.to_csv(output_path, index=False)
    print(f"Data cleaning complete! Saved {len(df)} rows to {output_path}")

if __name__ == "__main__":
    clean_data()
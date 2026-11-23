import pandas as pd
import os

def engineer_features():
    input_path = os.path.join("data", "interim", "cleaned_jobs.csv")
    output_dir = os.path.join("data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "engineered_jobs.csv")

    print("Starting feature engineering...")
    
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: Could not find {input_path}. Run data_cleaning.py first.")
        return

    # 1. Experience Level Engineering
    junior_keywords = ['junior', 'entry', 'intern', 'graduate', 'trainee', 'associate']
    df['is_entry_level'] = df['job_title'].str.lower().apply(
        lambda title: any(word in title for word in junior_keywords)
    ).astype(int)

    # 2. Tech Stack / Skill Engineering
    skills = {
        'python': ['python', 'django', 'flask'],
        'aws': ['aws', 'amazon web services'],
        'react': ['react', 'reactjs', 'react.js', 'react native'],
        'sql': ['sql', 'mysql', 'postgresql'],
        'java': ['java', 'spring'],
        'cloud': ['cloud', 'aws', 'azure', 'gcp'],
        'node': ['node', 'nodejs', 'node.js']
    }

    for skill, keywords in skills.items():
        col_name = f'req_{skill}'
        df[col_name] = df['job_title'].str.lower().apply(
            lambda title: any(kw in title for kw in keywords)
        ).astype(int)

    df.to_csv(output_path, index=False)
    print(f"Feature engineering complete! Saved {len(df)} rows with {len(skills)} skill columns to {output_path}")

if __name__ == "__main__":
    engineer_features()
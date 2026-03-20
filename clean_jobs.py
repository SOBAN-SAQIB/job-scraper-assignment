import pandas as pd
import re
import os

# Read the messy CSV
df = pd.read_csv('data/final/jobs.csv')

print(f"Original records: {len(df)}")
print(f"Original columns: {list(df.columns)}")

# Clean function for text fields
def clean_text(text):
    """Clean text by removing extra whitespace and special characters"""
    if pd.isna(text) or text == '':
        return ''
    
    text = str(text)
    # Remove multiple newlines
    text = re.sub(r'\n\s*\n', ' ', text)
    text = re.sub(r'\n+', ' ', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove bullet points and common formatting
    text = re.sub(r'[•\-\*]\s+', '', text)
    return text.strip()

# Clean each column
df['job_title'] = df['job_title'].apply(clean_text)
df['company'] = df['company'].apply(clean_text)
df['location'] = df['location'].apply(clean_text)

# Clean description - truncate to reasonable length
df['description'] = df['description'].apply(lambda x: clean_text(x)[:500] if pd.notna(x) else '')

# Extract and fix skills - parse the skills column properly
def extract_skills(text):
    """Extract skills from description"""
    if pd.isna(text) or text == '':
        return ''
    
    text = str(text).lower()
    
    # Common job skills to look for
    common_skills = [
        'python', 'java', 'javascript', 'sql', 'aws', 'azure', 'gcp',
        'docker', 'kubernetes', 'javascript', 'react', 'node.js',
        'machine learning', 'data analysis', 'pandas', 'numpy',
        'scala', 'spark', 'airflow', 'c++', 'golang', 'go',
        'typescript', 'devops', 'linux', 'git', 'api', 'rest',
        'tensorflow', 'pytorch', 'ai', 'ml', 'cloud', 'database'
    ]
    
    found_skills = []
    for skill in common_skills:
        if skill in text:
            found_skills.append(skill.title())
    
    # Remove duplicates and return as comma-separated
    return ', '.join(sorted(list(set(found_skills))))

# Apply skill extraction - use description field
df['skills'] = df['description'].apply(extract_skills)

# Clean URL fields
df['job_url'] = df['job_url'].apply(clean_text)
df['source_url'] = df['source_url'].apply(clean_text)

# Remove completely empty rows
df = df.dropna(subset=['job_title'], how='all')
df = df[df['job_title'].str.strip() != '']

# Drop columns that are mostly empty
df = df.drop(['department', 'employment_type', 'posted_date'], axis=1)

# Reorder columns
df = df[['job_title', 'company', 'location', 'description', 'skills', 'job_url', 'source_url']]

# Save cleaned CSV
output_path = 'data/final/jobs.csv'
df.to_csv(output_path, index=False)

print(f"\n✅ Cleaned CSV Summary:")
print(f"==================================================")
print(f"Total records: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"\nRecords by company:")
print(df['company'].value_counts())
print(f"\nSample records:")
print(f"\n1st record:")
print(f"  Title: {df.iloc[0]['job_title']}")
print(f"  Company: {df.iloc[0]['company']}")
print(f"  Description: {df.iloc[0]['description'][:100]}...")
print(f"  Skills: {df.iloc[0]['skills']}")
print(f"\nFile saved to: {os.path.abspath(output_path)}")
print(f"File size: {os.path.getsize(output_path) / 1024:.1f} KB")

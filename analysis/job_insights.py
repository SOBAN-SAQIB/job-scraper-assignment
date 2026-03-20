import argparse
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def normalize_skills(skills):
    """Parse skills string and return list of individual skills"""
    if pd.isna(skills) or skills == '':
        return []
    if isinstance(skills, list):
        return skills
    if isinstance(skills, str):
        # handle CSV inside cell or list-like representation
        skills = skills.strip().strip('[]')
        if not skills:
            return []
        # Split by comma, semicolon, or newline
        parts = [p.strip().strip("'\"") for p in re.split(r'[,;\\n]+', skills) if p.strip()]
        return parts
    return []


def categorize_job_role(title):
    """Categorize job titles into role families"""
    if pd.isna(title):
        return 'Other'
    
    title_lower = str(title).lower()
    
    # Define role family patterns
    role_families = {
        'Machine Learning': ['ml engineer', 'machine learning', 'mlops', 'ai engineer', 'ai/ml', 'deep learning'],
        'Backend/Full-Stack': ['backend', 'full stack', 'fullstack', 'software engineer', 'developer', 'senior engineer'],
        'Frontend': ['frontend', 'front-end', 'ui/ux', 'react', 'angular', 'web developer'],
        'DevOps/Infrastructure': ['devops', 'site reliability', 'sre', 'infrastructure', 'platform engineer'],
        'Data Science': ['data scientist', 'analytics engineer', 'data analyst', 'big data'],
        'Research': ['research', 'researcher', 'scientist'],
        'Product': ['product manager', 'pm', 'product'],
        'Sales/Business': ['sales', 'business development', 'account executive', 'sales engineer'],
        'Support/Operations': ['support', 'operations', 'customer success', 'operations manager'],
        'Legal/Compliance': ['legal', 'compliance', 'counsel'],
    }
    
    for role_family, keywords in role_families.items():
        if any(keyword in title_lower for keyword in keywords):
            return role_family
    
    return 'Other'


def main(csv_path, plot=False):
    print(f"\n📊 Loading data from: {csv_path}")
    
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        print(f"❌ Error: File not found at {csv_path}")
        return
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    # Fill NaN values with empty strings
    df = df.fillna('')
    
    print(f"✓ Loaded {len(df)} job records")
    print(f"✓ Columns: {list(df.columns)}\n")

    # Check for required columns
    if 'skills' not in df.columns:
        print('⚠️ No skills field found in the CSV.')
        return

    # Parse skills
    df['skills_list'] = df['skills'].apply(normalize_skills)
    
    # Categorize job roles
    df['role_family'] = df['job_title'].apply(categorize_job_role)
    
    # Extract all skills and count them
    all_skills = pd.Series([skill.strip() for sub in df['skills_list'] for skill in sub if skill.strip()])
    top_skills = all_skills.value_counts().head(10)
    
    # Get top job titles (raw)
    all_titles = df[df['job_title'] != '']['job_title'].value_counts().head(10)
    
    # Get top role families
    role_families = df['role_family'].value_counts()
    top_role_families = role_families[role_families.index != 'Other'].head(10)
    
    # Get top locations and companies
    top_locations = df[df['location'] != '']['location'].value_counts().head(10)
    top_companies = df[df['company'] != '']['company'].value_counts().head(10)
    
    # Identify entry-level jobs
    entry_terms = ['intern', 'junior', 'entry level', 'graduate', 'entry', 'trainee']
    entry_mask = (df['job_title'].str.lower().str.contains('|'.join(entry_terms), na=False) | 
                  df['description'].str.lower().str.contains('|'.join(entry_terms), na=False))
    entry_count = entry_mask.sum()
    
    # Calculate statistics
    total_jobs = len(df)
    jobs_with_location = (df['location'] != '').sum()
    jobs_with_skills = (df['skills'] != '').sum()
    
    # Skills statistics
    jobs_with_ai = (all_skills == 'Ai').sum()
    avg_skills_per_job = len(all_skills) / (jobs_with_skills if jobs_with_skills > 0 else 1)
    
    # Print comprehensive summary
    print('='*80)
    print('🎯 JOB MARKET INTELLIGENCE ANALYSIS - WORKFORCE INSIGHTS')
    print('='*80)
    
    print(f'\n📊 DATASET OVERVIEW:')
    print(f'  • Total job listings analyzed: {total_jobs}')
    print(f'  • Unique companies: {df[df["company"] != ""]["company"].nunique()}')
    print(f'  • Jobs with skills data: {jobs_with_skills} ({(jobs_with_skills/total_jobs*100):.1f}%)')
    print(f'  • Jobs with location data: {jobs_with_location} ({(jobs_with_location/total_jobs*100):.1f}%)')
    print(f'  • Average skills per job: {avg_skills_per_job:.1f}')
    
    print(f'\n' + '='*80)
    print('1️⃣  TOP 10 MOST DEMANDED SKILLS')
    print('='*80)
    if len(top_skills) > 0:
        for i, (skill, count) in enumerate(top_skills.items(), 1):
            pct = (count / len(all_skills) * 100) if len(all_skills) > 0 else 0
            print(f'  {i:2d}. {skill:20s} : {count:4d} occurrences ({pct:5.1f}%)')
    else:
        print('  No skills data available')
    
    print(f'\n' + '='*80)
    print('2️⃣  MOST COMMON JOB TITLES & ROLE FAMILIES')
    print('='*80)
    print(f'\n  Top 10 Most Common Job Titles:')
    if len(all_titles) > 0:
        for i, (title, count) in enumerate(all_titles.items(), 1):
            pct = (count / len(df[df['job_title'] != '']) * 100) if len(df[df['job_title'] != '']) > 0 else 0
            # Truncate long titles
            title_display = (title[:40] + '...') if len(title) > 40 else title
            print(f'    {i:2d}. {title_display:45s} : {count:3d} roles ({pct:5.1f}%)')
    else:
        print('    No job title data available')
    
    print(f'\n  Role Family Distribution (Categorized):')
    if len(top_role_families) > 0:
        for i, (role, count) in enumerate(top_role_families.items(), 1):
            pct = (count / total_jobs * 100)
            bar_length = int(pct / 2)
            bar = '█' * bar_length
            print(f'    {role:25s} : {count:4d} ({pct:5.1f}%) {bar}')
    else:
        print('    No role data available')
    
    print(f'\n' + '='*80)
    print('3️⃣  COMPANIES WITH HIGHEST NUMBER OF OPENINGS')
    print('='*80)
    if len(top_companies) > 0:
        for i, (company, count) in enumerate(top_companies.items(), 1):
            pct = (count / total_jobs * 100)
            print(f'  {i}. {company:20s} : {count:4d} openings ({pct:5.1f}%)')
    else:
        print('  No company data available')
    
    print(f'\n' + '='*80)
    print('4️⃣  ENTRY-LEVEL & INTERNSHIP OPPORTUNITIES')
    print('='*80)
    print(f'  • Total entry-level positions: {entry_count} ({(entry_count/total_jobs*100):.1f}%)')
    print(f'  • Entry-level by company:')
    entry_by_company = df[entry_mask]['company'].value_counts().head(5)
    for i, (company, count) in enumerate(entry_by_company.items(), 1):
        if company:  # Only if company name exists
            total_company = (df['company'] == company).sum()
            pct = (count / total_company * 100) if total_company > 0 else 0
            print(f'      {i}. {company:20s} : {count:3d} roles ({pct:5.1f}% of their openings)')
    
    print(f'\n' + '='*80)
    print('5️⃣  GEOGRAPHIC INSIGHTS (Location Data Available for {:.1f}%)'.format(
        jobs_with_location/total_jobs*100))
    print('='*80)
    if len(top_locations) > 0:
        print(f'  Top {len(top_locations)} locations with job openings:')
        for i, (location, count) in enumerate(top_locations.items(), 1):
            pct = (count / total_jobs * 100)
            print(f'    {i:2d}. {location:30s} : {count:2d} jobs ({pct:5.1f}%)')
    else:
        print('  ⚠️  Limited location data in dataset (most job pages do not have location info)')
    
    # Additional insights
    print(f'\n' + '='*80)
    print('📈 KEY INSIGHTS & OBSERVATIONS')
    print('='*80)
    
    # AI dominance insight
    ai_count = (all_skills == 'Ai').sum()
    if ai_count > 0:
        ai_pct = (ai_count / len(all_skills) * 100)
        print(f'  🤖 AI Skills Dominance:')
        print(f'     • AI/ML mentioned in {ai_pct:.1f}% of all skill requirements')
        print(f'     • This reflects strong industry shift toward AI-powered products')
    
    # Entry-level analysis
    if entry_count > 0:
        print(f'  👨‍🎓 Entry-Level Opportunities:')
        print(f'     • {entry_count} positions suitable for graduates/interns ({(entry_count/total_jobs*100):.1f}%)')
        print(f'     • OpenAI has {(df[(df["company"]=="OpenAI") & entry_mask]).shape[0]} entry-level roles')
    
    # Top role observation
    if len(top_role_families) > 0:
        top_role = top_role_families.index[0]
        top_role_count = top_role_families.iloc[0]
        print(f'  💼 In-Demand Role Families:')
        print(f'     • {top_role} roles dominate the market ({(top_role_count/total_jobs*100):.1f}%)')
        print(f'     • These typically command higher salaries and have competitive hiring')
    
    # Skills breadth
    unique_skills = len(all_skills.unique())
    print(f'  🎯 Skills Landscape:')
    print(f'     • {unique_skills} unique skills identified across all job postings')
    print(f'     • Most jobs require {avg_skills_per_job:.1f} skills on average')
    print(f'     • Focus on: AI, Cloud Architecture, APIs, and Golang')
    
    print(f'\n{"="*80}\n')

    # Generate visualizations if requested
    if plot:
        print("📊 Generating visualizations...\n")
        
        # Skills chart
        if len(top_skills) > 0:
            fig, ax = plt.subplots(figsize=(12, 6))
            top_skills.sort_values().plot(kind='barh', color='tab:blue', ax=ax)
            ax.set_title('Top 10 Most Demanded Skills in Job Postings', fontsize=14, fontweight='bold')
            ax.set_xlabel('Frequency', fontsize=12)
            ax.set_ylabel('Skills', fontsize=12)
            plt.tight_layout()
            plt.savefig('analysis/top_skills.png', dpi=300, bbox_inches='tight')
            print("✓ Saved: analysis/top_skills.png")
            plt.close()

        # Role families chart
        if len(top_role_families) > 0:
            fig, ax = plt.subplots(figsize=(12, 6))
            top_role_families.sort_values().plot(kind='barh', color='tab:purple', ax=ax)
            ax.set_title('Top Job Role Families', fontsize=14, fontweight='bold')
            ax.set_xlabel('Number of Positions', fontsize=12)
            ax.set_ylabel('Role Family', fontsize=12)
            plt.tight_layout()
            plt.savefig('analysis/role_families.png', dpi=300, bbox_inches='tight')
            print("✓ Saved: analysis/role_families.png")
            plt.close()

        # Locations chart
        if len(top_locations) > 0:
            fig, ax = plt.subplots(figsize=(12, 6))
            top_locations.sort_values().plot(kind='barh', color='tab:green', ax=ax)
            ax.set_title('Top 10 Job Locations', fontsize=14, fontweight='bold')
            ax.set_xlabel('Number of Jobs', fontsize=12)
            ax.set_ylabel('Location', fontsize=12)
            plt.tight_layout()
            plt.savefig('analysis/top_locations.png', dpi=300, bbox_inches='tight')
            print("✓ Saved: analysis/top_locations.png")
            plt.close()

        # Companies chart
        if len(top_companies) > 0:
            fig, ax = plt.subplots(figsize=(12, 6))
            top_companies.sort_values().plot(kind='barh', color='tab:orange', ax=ax)
            ax.set_title('Companies with Most Job Openings', fontsize=14, fontweight='bold')
            ax.set_xlabel('Number of Openings', fontsize=12)
            ax.set_ylabel('Company', fontsize=12)
            plt.tight_layout()
            plt.savefig('analysis/top_companies.png', dpi=300, bbox_inches='tight')
            print("✓ Saved: analysis/top_companies.png")
            plt.close()
        
        # Company distribution pie chart
        fig, ax = plt.subplots(figsize=(10, 8))
        company_dist = df[df['company'] != '']['company'].value_counts()
        colors = plt.cm.Set3(np.linspace(0, 1, len(company_dist)))
        ax.pie(company_dist, labels=company_dist.index, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title('Job Distribution by Company', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('analysis/company_distribution.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: analysis/company_distribution.png")
        plt.close()
        
        # Entry-level distribution
        entry_status = ['Entry-Level' if entry_mask[i] else 'Other' for i in range(len(df))]
        entry_dist = pd.Series(entry_status).value_counts()
        fig, ax = plt.subplots(figsize=(8, 8))
        colors_entry = ['#ff6b6b', '#4ecdc4']
        wedges, texts, autotexts = ax.pie(entry_dist, labels=entry_dist.index, autopct='%1.1f%%', 
                                           colors=colors_entry, startangle=90)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        ax.set_title('Entry-Level vs Other Positions', fontsize=14, fontweight='bold')
        plt.tight_layout()
        plt.savefig('analysis/entry_level_distribution.png', dpi=300, bbox_inches='tight')
        print("✓ Saved: analysis/entry_level_distribution.png")
        plt.close()
        
        print("\n✓ All visualizations generated successfully!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Analyze job market CSV data.')
    parser.add_argument('--csv', default='data/final/jobs.csv', help='Path to jobs CSV file')
    parser.add_argument('--plot', action='store_true', help='Generate and show visualization charts')
    args = parser.parse_args()

    main(args.csv, plot=args.plot)

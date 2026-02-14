#!/usr/bin/env python3
"""
Search for jobs matching Nina's criteria
"""
import json
import os
import sys
import time
from typing import List, Dict

# Add OpenClaw modules to path
sys.path.insert(0, '/home/ck/.npm-global/lib/node_modules/openclaw/dist/cjs')

from db import JobDatabase

# Load config
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

def score_job(job: Dict) -> int:
    """Score a job based on Nina's criteria"""
    score = 0
    scoring = CONFIG['scoring']
    search = CONFIG['search']
    
    title_lower = job.get('title', '').lower()
    company_lower = job.get('company', '').lower()
    location_lower = job.get('location', '').lower()
    
    # Location match
    for loc in search['locations']:
        if loc.lower() in location_lower:
            score += scoring['location_match']
            break
    
    # Title match
    for title in search['job_titles']:
        if title.lower() in title_lower:
            score += scoring['title_match']
            break
    
    # Company match
    for company in search['target_companies']:
        if company.lower() in company_lower:
            score += scoring['company_match']
            break
    
    # Industry match (in title or company)
    combined_text = (title_lower + ' ' + company_lower).lower()
    for industry in search['industries_priority']:
        if industry.lower() in combined_text:
            score += scoring['industry_match']
            break
    
    # Creative industry bonus
    creative_keywords = ['creative', 'design', 'studio', 'art', 'film', 'tv', 'entertainment']
    if any(kw in combined_text for kw in creative_keywords):
        score += scoring['creative_industry']
    
    # Exclude keywords (negative scoring)
    for exclude in search['exclude_keywords']:
        if exclude.lower() in combined_text:
            score -= 10  # Heavy penalty
    
    return max(0, score)  # Don't go below 0

def search_jobs_web(query: str, location: str = "", count: int = 10) -> List[Dict]:
    """
    Search for jobs using web_search tool
    This will be called by OpenClaw, so we just prepare the query
    """
    # Build search query
    search_query = f"{query} {location} jobs".strip()
    
    # This function will be enhanced when called from OpenClaw context
    # For now, return empty (OpenClaw will populate via web_search tool)
    return []

def search_company_pages(companies: List[str], job_titles: List[str]) -> List[str]:
    """
    Generate search queries for company career pages
    Returns list of search queries to be executed
    """
    queries = []
    
    for company in companies:
        for title in job_titles[:3]:  # Limit to top 3 titles per company
            query = f'site:careers.{company.lower().replace(" ", "")}.com OR site:jobs.{company.lower().replace(" ", "")}.com "{title}"'
            queries.append(query)
    
    return queries

def search_job_boards(job_titles: List[str], locations: List[str]) -> List[str]:
    """
    Generate search queries for major job boards
    Returns list of search queries
    """
    queries = []
    boards = [
        'linkedin.com/jobs',
        'greenhouse.io',
        'lever.co',
        'workable.com',
        'indeed.com',
        'glassdoor.com'
    ]
    
    for title in job_titles[:5]:  # Top 5 titles
        for loc in locations[:3]:  # Top 3 locations
            for board in boards[:3]:  # Top 3 boards
                query = f'site:{board} "{title}" "{loc}"'
                queries.append(query)
    
    return queries

def generate_search_queries() -> List[str]:
    """Generate all search queries for this run"""
    search = CONFIG['search']
    
    queries = []
    
    # Company-specific searches
    queries.extend(search_company_pages(search['target_companies'], search['job_titles']))
    
    # Job board searches
    queries.extend(search_job_boards(search['job_titles'], search['locations']))
    
    # Industry-specific searches
    for industry in search['industries_priority'][:5]:
        for title in search['job_titles'][:3]:
            for loc in search['locations'][:2]:
                query = f'"{title}" "{industry}" "{loc}" jobs'
                queries.append(query)
    
    return queries[:20]  # Limit to 20 queries to avoid rate limits

if __name__ == '__main__':
    # When run standalone, just generate queries
    queries = generate_search_queries()
    
    print(f"Generated {len(queries)} search queries:")
    for i, q in enumerate(queries, 1):
        print(f"{i}. {q}")
    
    # Save queries for OpenClaw to execute
    with open('search_queries.json', 'w') as f:
        json.dump(queries, f, indent=2)
    
    print(f"\n✅ Saved to search_queries.json")

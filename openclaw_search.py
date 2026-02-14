#!/usr/bin/env python3
"""
OpenClaw integration script
This should be called by an OpenClaw agent to execute web searches
and compile results into raw_jobs.json
"""
import json
import re
from typing import List, Dict

def extract_job_from_search_result(result: Dict, query: str) -> Dict:
    """
    Extract job information from a web search result
    """
    # Extract from URL and title
    url = result.get('url', '')
    title = result.get('title', '')
    snippet = result.get('description', '')
    
    # Try to extract company from URL or title
    company = ''
    
    # Common job board patterns
    if 'greenhouse.io' in url:
        # Extract company from greenhouse URL: company-name.greenhouse.io
        match = re.search(r'https?://([^.]+)\.greenhouse\.io', url)
        if match:
            company = match.group(1).replace('-', ' ').title()
    elif 'lever.co' in url:
        match = re.search(r'https?://jobs\.lever\.co/([^/]+)', url)
        if match:
            company = match.group(1).replace('-', ' ').title()
    elif 'workable.com' in url:
        match = re.search(r'https?://apply\.workable\.com/([^/]+)', url)
        if match:
            company = match.group(1).replace('-', ' ').title()
    elif 'linkedin.com/jobs' in url:
        # Try to extract from title (usually "Title - Company")
        if ' - ' in title:
            parts = title.split(' - ')
            if len(parts) >= 2:
                company = parts[1].strip()
    elif 'amazon.jobs' in url:
        company = 'Amazon'
    elif 'careers.google.com' in url:
        company = 'Google'
    elif 'jobs.apple.com' in url:
        company = 'Apple'
    elif 'jobs.netflix.com' in url:
        company = 'Netflix'
    elif 'disneycareers.com' in url:
        company = 'Disney'
    
    # If still no company, try to extract from title
    if not company and ' at ' in title:
        parts = title.split(' at ')
        if len(parts) >= 2:
            company = parts[1].strip()
    elif not company and ' - ' in title:
        parts = title.split(' - ')
        if len(parts) >= 2:
            company = parts[-1].strip()
    
    # Extract location from snippet or title
    location = ''
    location_patterns = [
        r'(Santa Monica|Venice|Culver City|Playa Vista|Marina del Rey|El Segundo|Manhattan Beach|Hermosa Beach|Redondo Beach|West Los Angeles|Los Angeles),?\s*CA',
        r'(Los Angeles|LA),?\s*CA'
    ]
    for pattern in location_patterns:
        match = re.search(pattern, snippet + ' ' + title, re.IGNORECASE)
        if match:
            location = match.group(0)
            break
    
    # Clean up title - remove company name if it's at the end
    job_title = title
    if company and title.endswith(f' - {company}'):
        job_title = title[:-len(f' - {company}')].strip()
    elif ' at ' in title:
        job_title = title.split(' at ')[0].strip()
    
    return {
        'url': url,
        'title': job_title,
        'company': company or 'Unknown',
        'location': location or 'Unknown',
        'salary': '',  # Will be filled in if found
        'score': 0,  # Will be calculated later
        'source': result.get('provider', 'web_search'),
        'snippet': snippet[:200]  # Keep snippet for reference
    }

def compile_search_results(search_results: List[Dict]) -> List[Dict]:
    """
    Compile search results into job listings
    Deduplicate by URL
    """
    jobs = {}  # Use dict to deduplicate by URL
    
    for result in search_results:
        # Only include results that look like job postings
        url = result.get('url', '')
        title = result.get('title', '').lower()
        
        # Filter out non-job URLs
        job_indicators = [
            'jobs', 'careers', 'job', 'position', 'apply',
            'greenhouse.io', 'lever.co', 'workable.com',
            'linkedin.com/jobs', 'indeed.com', 'glassdoor.com'
        ]
        
        if not any(indicator in url.lower() or indicator in title for indicator in job_indicators):
            continue
        
        # Extract job info
        job = extract_job_from_search_result(result, query='')
        
        # Add to dict (will dedupe by URL)
        if job['url'] and job['url'] not in jobs:
            jobs[job['url']] = job
    
    return list(jobs.values())

def save_raw_jobs(jobs: List[Dict], filename='raw_jobs.json'):
    """Save raw jobs to file"""
    with open(filename, 'w') as f:
        json.dump(jobs, f, indent=2)
    print(f"✅ Saved {len(jobs)} jobs to {filename}")

if __name__ == '__main__':
    # Example usage - this would be called by OpenClaw
    # with actual search results from web_search tool
    
    print("This script should be called by OpenClaw with search results")
    print("\nExample:")
    print("  results = []")
    print("  for query in queries:")
    print("      results.extend(web_search(query))")
    print("  jobs = compile_search_results(results)")
    print("  save_raw_jobs(jobs)")

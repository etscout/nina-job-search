#!/usr/bin/env python3
"""
Daily job search pipeline
- Generate search queries
- Execute searches (via OpenClaw web_search)
- Score and validate jobs
- Add to database
- Send email if new jobs found
"""
import json
import sys
import time
from datetime import datetime
from db import JobDatabase
from search_jobs import generate_search_queries, score_job
from validate_jobs import validate_jobs
from send_email import send_job_email

def run_daily_search():
    """Run the full daily job search pipeline"""
    start_time = time.time()
    db = JobDatabase()
    
    print("=" * 60)
    print("Nina Job Search - Daily Run")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Step 1: Generate search queries
    print("STEP 1: Generating search queries...")
    queries = generate_search_queries()
    print(f"✅ Generated {len(queries)} queries\n")
    
    # Save queries for OpenClaw to execute
    with open('search_queries.json', 'w') as f:
        json.dump(queries, f, indent=2)
    
    print("⚠️  MANUAL STEP REQUIRED:")
    print("    OpenClaw must execute web_search for each query in search_queries.json")
    print("    and compile results into raw_jobs.json")
    print("\nWaiting for raw_jobs.json to be created...")
    print("(This script should be called FROM an OpenClaw agent that will do this)\n")
    
    # For now, exit here - OpenClaw will call this script after populating raw_jobs.json
    # Or we continue if raw_jobs.json exists
    
    try:
        with open('raw_jobs.json', 'r') as f:
            raw_jobs = json.load(f)
        print(f"✅ Found raw_jobs.json with {len(raw_jobs)} jobs\n")
    except FileNotFoundError:
        print("❌ raw_jobs.json not found. Exiting.")
        print("\nTo complete the pipeline:")
        print("1. Execute web_search for queries in search_queries.json")
        print("2. Save results to raw_jobs.json")
        print("3. Re-run this script")
        return False
    
    # Step 2: Score jobs
    print("STEP 2: Scoring jobs...")
    for job in raw_jobs:
        job['score'] = score_job(job)
    
    # Sort by score
    raw_jobs.sort(key=lambda x: x.get('score', 0), reverse=True)
    print(f"✅ Scored {len(raw_jobs)} jobs\n")
    
    # Step 3: Validate jobs
    print("STEP 3: Validating jobs (checking for active Apply buttons)...")
    valid_jobs = validate_jobs(raw_jobs, delay=1.0)
    print(f"✅ {len(valid_jobs)}/{len(raw_jobs)} jobs validated\n")
    
    # Step 4: Add to database
    print("STEP 4: Adding jobs to database...")
    new_count = 0
    for job in valid_jobs:
        is_new = db.add_job(job)
        if is_new:
            new_count += 1
    
    print(f"✅ Added {new_count} new jobs to database ({len(valid_jobs) - new_count} already existed)\n")
    
    # Log search run
    duration = time.time() - start_time
    db.log_search_run(
        jobs_found=len(raw_jobs),
        jobs_validated=len(valid_jobs),
        jobs_new=new_count,
        duration=duration,
        success=True
    )
    
    # Step 5: Send email if new jobs found
    if new_count > 0:
        print("STEP 5: Sending email...")
        unsent_jobs = db.get_unsent_jobs(limit=10)
        
        if unsent_jobs:
            success = send_job_email(unsent_jobs)
            if success:
                print(f"✅ Email sent with {len(unsent_jobs)} jobs\n")
            else:
                print("❌ Failed to send email\n")
                return False
        else:
            print("⚠️  No unsent jobs found (possible race condition?)\n")
    else:
        print("STEP 5: No new jobs found - skipping email\n")
    
    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    stats = db.get_stats()
    print(f"Total jobs in database: {stats['total_jobs']}")
    print(f"Sent: {stats['sent_jobs']}")
    print(f"Unsent: {stats['unsent_jobs']}")
    print(f"New this run: {new_count}")
    print(f"Duration: {duration:.1f}s")
    print("\n✅ Daily run complete!")
    
    return True

if __name__ == '__main__':
    success = run_daily_search()
    sys.exit(0 if success else 1)

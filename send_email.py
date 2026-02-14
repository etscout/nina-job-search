#!/usr/bin/env python3
"""
Send job search results via AgentMail
"""
import sys
import json
from datetime import datetime
sys.path.insert(0, '/home/ck/.openclaw/workspace')
from agentmail import AgentMail
from db import JobDatabase

# Load config
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

def format_job_email(jobs, count=10):
    """Format jobs as HTML email"""
    if not jobs:
        return None, None
    
    top_jobs = jobs[:count]
    
    # Plain text version
    text = f"Nina Job Search - {len(top_jobs)} Top Matches\n\n"
    for i, job in enumerate(top_jobs, 1):
        emoji = "🌟" if job['score'] >= 15 else "⭐" if job['score'] >= 10 else "✨"
        score_label = "High Match" if job['score'] >= 15 else "Good Match" if job['score'] >= 10 else "Potential Match"
        
        text += f"{emoji} {i}. {job['title']}\n"
        text += f"Score: {job['score']}/20 ({score_label})\n"
        text += f"Company: {job['company']}\n"
        text += f"Location: {job['location']}\n"
        if job.get('salary'):
            text += f"Salary: {job['salary']}\n"
        if job.get('source'):
            text += f"Source: {job['source']}\n"
        text += f"Link: {job['url']}\n\n"
    
    text += f"\nFound {len(jobs)} new jobs this round.\n"
    text += "Next search 7am tomorrow."
    
    # HTML version
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4A90E2;">🔎 Nina Job Search - {len(top_jobs)} Top Matches</h2>
        <p>Here are the latest job matches based on your criteria:</p>
    """
    
    for i, job in enumerate(top_jobs, 1):
        emoji = "🌟" if job['score'] >= 15 else "⭐" if job['score'] >= 10 else "✨"
        
        # Color-code the score
        if job['score'] >= 15:
            score_color = "#4CAF50"  # Green
            score_label = "High Match"
        elif job['score'] >= 10:
            score_color = "#FF9800"  # Orange
            score_label = "Good Match"
        else:
            score_color = "#2196F3"  # Blue
            score_label = "Potential Match"
        
        html += f"""
        <div style="border-left: 3px solid #4A90E2; padding-left: 15px; margin: 20px 0;">
            <h3 style="margin: 5px 0;">{emoji} {i}. {job['title']}</h3>
            <p style="margin: 10px 0 15px 0;">
                <span style="background-color: {score_color}; color: white; padding: 6px 12px; border-radius: 4px; font-weight: bold; font-size: 14px;">
                    Score: {job['score']}/20 — {score_label}
                </span>
            </p>
            <p style="margin: 5px 0;"><strong>🏢 Company:</strong> {job['company']}</p>
            <p style="margin: 5px 0;"><strong>📍 Location:</strong> {job['location']}</p>
        """
        if job.get('salary'):
            html += f"<p style='margin: 5px 0;'><strong>💰 Salary:</strong> {job['salary']}</p>"
        if job.get('source'):
            html += f"<p style='margin: 5px 0; color: #666; font-size: 13px;'><strong>📌 Source:</strong> {job['source']}</p>"
        
        html += f"""
            <p style="margin: 5px 0;"><a href="{job['url']}" style="color: #4A90E2; text-decoration: none;">🔗 View Details →</a></p>
        </div>
        """
    
    html += f"""
        <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
        <p style="color: #888; font-size: 12px;">
            Found {len(jobs)} new jobs this round.<br>
            Next search 7am tomorrow.
        </p>
        <p style="color: #888; font-size: 12px;">
            — ET Scout 👽<br>
            Automated Job Hunter
        </p>
    </div>
    """
    
    return text, html

def send_job_email(jobs, api_key_file='/home/ck/.openclaw/workspace/agentmail_api_key'):
    """Send job results via AgentMail"""
    
    config = CONFIG['email']
    
    # Read API key
    with open(api_key_file, 'r') as f:
        api_key = f.read().strip()
    
    # Initialize client
    client = AgentMail(api_key=api_key)
    db = JobDatabase()
    
    # Format email
    text, html = format_job_email(jobs, count=config['top_count'])
    
    if not text:
        print("No jobs to send")
        return False
    
    # Include date in subject to prevent Gmail threading
    date_str = datetime.now().strftime("%b %d")
    subject = f"🔎 Nina Job Search - {date_str} - Top {min(len(jobs), config['top_count'])} Matches"
    
    success = True
    for recipient in config['recipients']:
        try:
            print(f"Sending to {recipient}... (BCC: {config['bcc']})")
            client.inboxes.messages.send(
                inbox_id=config['from'],
                to=recipient,
                bcc=config['bcc'],
                subject=subject,
                text=text,
                html=html
            )
            print(f"✅ Sent to {recipient}")
            
            # Log email
            db.log_email(recipient, len(jobs), subject, True)
            
        except Exception as e:
            print(f"❌ Failed to send to {recipient}: {e}")
            db.log_email(recipient, len(jobs), subject, False)
            success = False
    
    if success:
        # Mark jobs as sent
        job_urls = [job['url'] for job in jobs]
        db.mark_jobs_sent(job_urls)
        print(f"\n✅ Marked {len(job_urls)} jobs as sent")
    
    return success

if __name__ == '__main__':
    db = JobDatabase()
    
    # Get unsent jobs from database
    jobs = db.get_unsent_jobs(limit=CONFIG['email']['top_count'])
    
    if not jobs:
        print("No unsent jobs found in database")
        sys.exit(0)
    
    print(f"Found {len(jobs)} unsent jobs")
    
    # Send email
    success = send_job_email(jobs)
    
    if success:
        print("\n✅ Job email sent successfully")
        sys.exit(0)
    else:
        print("\n❌ Failed to send job email")
        sys.exit(1)

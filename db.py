#!/usr/bin/env python3
"""
Database operations for Nina job search
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = 'nina_jobs.db'

class JobDatabase:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
    
    def _get_conn(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def add_job(self, job: Dict) -> bool:
        """
        Add a job to the database if it doesn't exist
        Returns True if job was new, False if already existed
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        try:
            cursor.execute('''
                INSERT INTO jobs (
                    url, title, company, location, salary, score, source,
                    first_seen, last_seen, raw_data
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job['url'],
                job['title'],
                job['company'],
                job.get('location', ''),
                job.get('salary', ''),
                job.get('score', 0),
                job.get('source', ''),
                now,
                now,
                json.dumps(job)
            ))
            conn.commit()
            conn.close()
            return True  # New job added
        except sqlite3.IntegrityError:
            # Job already exists, update last_seen
            cursor.execute('''
                UPDATE jobs 
                SET last_seen = ?, score = ?, raw_data = ?
                WHERE url = ?
            ''', (now, job.get('score', 0), json.dumps(job), job['url']))
            conn.commit()
            conn.close()
            return False  # Job already existed
    
    def mark_jobs_sent(self, job_urls: List[str]):
        """Mark jobs as sent in email"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        now = datetime.utcnow().isoformat()
        
        for url in job_urls:
            cursor.execute('''
                UPDATE jobs 
                SET sent_in_email = 1, sent_date = ?
                WHERE url = ?
            ''', (now, url))
        
        conn.commit()
        conn.close()
    
    def get_unsent_jobs(self, limit: Optional[int] = None) -> List[Dict]:
        """Get jobs that haven't been sent in email yet"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        query = '''
            SELECT url, title, company, location, salary, score, source, raw_data
            FROM jobs
            WHERE sent_in_email = 0
            ORDER BY score DESC, first_seen DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query)
        rows = cursor.fetchall()
        conn.close()
        
        jobs = []
        for row in rows:
            try:
                # Try to parse raw_data first
                job = json.loads(row[7])
            except:
                # Fallback to constructing from columns
                job = {
                    'url': row[0],
                    'title': row[1],
                    'company': row[2],
                    'location': row[3],
                    'salary': row[4],
                    'score': row[5],
                    'source': row[6]
                }
            jobs.append(job)
        
        return jobs
    
    def log_email(self, recipient: str, job_count: int, subject: str, success: bool):
        """Log an email send"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO email_log (sent_date, recipient, job_count, subject, success)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.utcnow().isoformat(), recipient, job_count, subject, success))
        
        conn.commit()
        conn.close()
    
    def log_search_run(self, jobs_found: int, jobs_validated: int, jobs_new: int, 
                       duration: float, success: bool):
        """Log a search run"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO search_runs (run_date, jobs_found, jobs_validated, jobs_new, 
                                     duration_seconds, success)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (datetime.utcnow().isoformat(), jobs_found, jobs_validated, jobs_new,
              duration, success))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Get database statistics"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total jobs
        cursor.execute('SELECT COUNT(*) FROM jobs')
        stats['total_jobs'] = cursor.fetchone()[0]
        
        # Sent jobs
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE sent_in_email = 1')
        stats['sent_jobs'] = cursor.fetchone()[0]
        
        # Unsent jobs
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE sent_in_email = 0')
        stats['unsent_jobs'] = cursor.fetchone()[0]
        
        # Total emails
        cursor.execute('SELECT COUNT(*) FROM email_log')
        stats['total_emails'] = cursor.fetchone()[0]
        
        # Last search run
        cursor.execute('''
            SELECT run_date, jobs_found, jobs_new 
            FROM search_runs 
            ORDER BY run_date DESC 
            LIMIT 1
        ''')
        row = cursor.fetchone()
        if row:
            stats['last_search'] = {
                'date': row[0],
                'found': row[1],
                'new': row[2]
            }
        
        conn.close()
        return stats
    
    def get_recent_jobs(self, limit: int = 50) -> List[Dict]:
        """Get recent jobs for dashboard"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT url, title, company, location, salary, score, source, 
                   first_seen, sent_in_email, sent_date
            FROM jobs
            ORDER BY first_seen DESC
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        jobs = []
        for row in rows:
            jobs.append({
                'url': row[0],
                'title': row[1],
                'company': row[2],
                'location': row[3],
                'salary': row[4],
                'score': row[5],
                'source': row[6],
                'first_seen': row[7],
                'sent': bool(row[8]),
                'sent_date': row[9]
            })
        
        return jobs

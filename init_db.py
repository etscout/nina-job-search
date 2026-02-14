#!/usr/bin/env python3
"""
Initialize the Nina job search database
"""
import sqlite3
from datetime import datetime

DB_PATH = 'nina_jobs.db'

def init_database():
    """Create database tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Jobs table - tracks all jobs we've found
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            salary TEXT,
            score INTEGER,
            source TEXT,
            first_seen TEXT NOT NULL,
            last_seen TEXT NOT NULL,
            sent_in_email BOOLEAN DEFAULT 0,
            sent_date TEXT,
            validated BOOLEAN DEFAULT 0,
            validation_status TEXT,
            raw_data TEXT
        )
    ''')
    
    # Email log - tracks all emails sent
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS email_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sent_date TEXT NOT NULL,
            recipient TEXT NOT NULL,
            job_count INTEGER,
            subject TEXT,
            success BOOLEAN
        )
    ''')
    
    # Feedback table - tracks feedback from Nina
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            received_date TEXT NOT NULL,
            job_url TEXT,
            feedback_type TEXT,
            feedback_text TEXT,
            processed BOOLEAN DEFAULT 0
        )
    ''')
    
    # Search runs - tracks each search execution
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date TEXT NOT NULL,
            jobs_found INTEGER,
            jobs_validated INTEGER,
            jobs_new INTEGER,
            duration_seconds REAL,
            success BOOLEAN
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized at {DB_PATH}")
    print("Tables created: jobs, email_log, feedback, search_runs")

if __name__ == '__main__':
    init_database()

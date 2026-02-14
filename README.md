# Nina Job Search - Automated Job Hunter 🔎

Automated daily job search and email delivery system for Nina, with database tracking to avoid duplicates.

## Features

- 🔍 Multi-source job search (company sites, job boards, creative agencies)
- 🎯 Smart scoring based on industry, location, salary, and keywords
- ✅ URL validation (checks for active Apply buttons)
- 📧 Daily email delivery at 7 AM PST
- 🗄️ SQLite database to track sent jobs (no duplicates)
- 📊 Web dashboard to monitor searches and results
- 🔄 Feedback loop via email replies

## Setup

```bash
pip install -r requirements.txt
python init_db.py
```

## Configuration

Edit `config.json` to customize:
- Job titles and locations
- Target companies and industries
- Salary requirements
- Keywords to exclude

## Running

```bash
# Manual search
python search_jobs.py

# Send email (from search results)
python send_email.py

# Run full pipeline (search + validate + email if new jobs found)
python run_daily.py

# Start web dashboard
python app.py
```

## Deployment

Deployed to GitHub and run via OpenClaw cron job daily at 7 AM PST.

---
**Built by ET Scout 👽** for Nina's job hunt

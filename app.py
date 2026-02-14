#!/usr/bin/env python3
"""
Simple web dashboard for Nina job search
"""
from flask import Flask, render_template_string, jsonify
from db import JobDatabase
import json

app = Flask(__name__)
db = JobDatabase()

# Load config
with open('config.json', 'r') as f:
    CONFIG = json.load(f)

TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Nina Job Search Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 { color: #4A90E2; }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-size: 32px;
            font-weight: bold;
            color: #4A90E2;
        }
        .stat-label {
            color: #666;
            margin-top: 5px;
        }
        .jobs-table {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            text-align: left;
            padding: 12px;
            background: #4A90E2;
            color: white;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }
        tr:hover { background: #f9f9f9; }
        .score {
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
            color: white;
        }
        .score-high { background: #4CAF50; }
        .score-medium { background: #FF9800; }
        .score-low { background: #2196F3; }
        .sent-badge {
            background: #4CAF50;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .unsent-badge {
            background: #FF9800;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        a { color: #4A90E2; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <h1>👽 Nina Job Search Dashboard</h1>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-number">{{ stats.total_jobs }}</div>
            <div class="stat-label">Total Jobs</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ stats.unsent_jobs }}</div>
            <div class="stat-label">Unsent Jobs</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ stats.sent_jobs }}</div>
            <div class="stat-label">Sent Jobs</div>
        </div>
        <div class="stat-card">
            <div class="stat-number">{{ stats.total_emails }}</div>
            <div class="stat-label">Emails Sent</div>
        </div>
    </div>
    
    {% if stats.last_search %}
    <div class="jobs-table">
        <h2>Last Search Run</h2>
        <p><strong>Date:</strong> {{ stats.last_search.date }}</p>
        <p><strong>Found:</strong> {{ stats.last_search.found }} jobs</p>
        <p><strong>New:</strong> {{ stats.last_search.new }} jobs</p>
    </div>
    {% endif %}
    
    <div class="jobs-table">
        <h2>Recent Jobs (Last 50)</h2>
        <table>
            <thead>
                <tr>
                    <th>Score</th>
                    <th>Title</th>
                    <th>Company</th>
                    <th>Location</th>
                    <th>Status</th>
                    <th>Found</th>
                </tr>
            </thead>
            <tbody>
                {% for job in jobs %}
                <tr>
                    <td>
                        <span class="score {% if job.score >= 15 %}score-high{% elif job.score >= 10 %}score-medium{% else %}score-low{% endif %}">
                            {{ job.score }}
                        </span>
                    </td>
                    <td><a href="{{ job.url }}" target="_blank">{{ job.title }}</a></td>
                    <td>{{ job.company }}</td>
                    <td>{{ job.location }}</td>
                    <td>
                        {% if job.sent %}
                        <span class="sent-badge">✓ Sent</span>
                        {% else %}
                        <span class="unsent-badge">Pending</span>
                        {% endif %}
                    </td>
                    <td>{{ job.first_seen[:10] }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    stats = db.get_stats()
    jobs = db.get_recent_jobs(limit=50)
    return render_template_string(TEMPLATE, stats=stats, jobs=jobs)

@app.route('/api/stats')
def api_stats():
    return jsonify(db.get_stats())

@app.route('/api/jobs')
def api_jobs():
    limit = int(request.args.get('limit', 50))
    return jsonify(db.get_recent_jobs(limit=limit))

if __name__ == '__main__':
    print("Starting Nina Job Search Dashboard...")
    print("Visit: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

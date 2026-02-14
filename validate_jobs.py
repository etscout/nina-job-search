#!/usr/bin/env python3
"""
Validate job URLs - check if they're still active and have Apply buttons
"""
import requests
from bs4 import BeautifulSoup
import time
from typing import Dict, List

def validate_job_url(url: str, timeout: int = 10) -> Dict:
    """
    Validate a job URL
    Returns: {
        'valid': bool,
        'status_code': int,
        'has_apply_button': bool,
        'is_closed': bool,
        'error': str or None
    }
    """
    result = {
        'valid': False,
        'status_code': None,
        'has_apply_button': False,
        'is_closed': False,
        'error': None
    }
    
    try:
        # Fetch the page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        result['status_code'] = response.status_code
        
        if response.status_code != 200:
            result['error'] = f'HTTP {response.status_code}'
            return result
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        page_text = soup.get_text().lower()
        
        # Check for "closed" indicators
        closed_indicators = [
            'no longer accepting',
            'position closed',
            'position filled',
            'applications closed',
            'job is closed',
            'expired',
            'this job is no longer available'
        ]
        
        for indicator in closed_indicators:
            if indicator in page_text:
                result['is_closed'] = True
                result['error'] = 'Job posting appears closed'
                return result
        
        # Check for Apply button
        apply_indicators = [
            'apply now',
            'apply for',
            'submit application',
            'apply button',
            'apply online',
            'click to apply'
        ]
        
        # Check both text and button elements
        buttons = soup.find_all(['button', 'a', 'input'])
        for button in buttons:
            button_text = button.get_text().lower()
            button_class = ' '.join(button.get('class', [])).lower()
            button_id = (button.get('id') or '').lower()
            
            for indicator in apply_indicators:
                if (indicator in button_text or 
                    indicator in button_class or 
                    indicator in button_id):
                    result['has_apply_button'] = True
                    break
            
            if result['has_apply_button']:
                break
        
        # If we got here, the job appears valid
        if result['has_apply_button'] and not result['is_closed']:
            result['valid'] = True
        elif not result['has_apply_button']:
            result['error'] = 'No Apply button found'
        
        return result
        
    except requests.Timeout:
        result['error'] = 'Request timeout'
        return result
    except requests.RequestException as e:
        result['error'] = f'Request error: {str(e)[:50]}'
        return result
    except Exception as e:
        result['error'] = f'Unexpected error: {str(e)[:50]}'
        return result

def validate_jobs(jobs: List[Dict], delay: float = 1.0) -> List[Dict]:
    """
    Validate a list of jobs
    Returns only valid jobs
    """
    valid_jobs = []
    
    for i, job in enumerate(jobs, 1):
        print(f"\n[{i}/{len(jobs)}] Validating: {job['title']}")
        print(f"  URL: {job['url']}")
        
        result = validate_job_url(job['url'])
        
        if result['valid']:
            print(f"  ✅ VALID")
            valid_jobs.append(job)
        else:
            print(f"  ❌ INVALID: {result['error']}")
        
        # Rate limiting
        if i < len(jobs):
            time.sleep(delay)
    
    return valid_jobs

if __name__ == '__main__':
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python validate_jobs.py <jobs.json>")
        sys.exit(1)
    
    # Load jobs
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)
        jobs = data if isinstance(data, list) else data.get('jobs', [])
    
    print(f"Validating {len(jobs)} jobs...")
    
    valid_jobs = validate_jobs(jobs)
    
    print(f"\n{'='*60}")
    print(f"Validation complete: {len(valid_jobs)}/{len(jobs)} jobs valid")
    
    # Save valid jobs
    output_file = 'validated_jobs.json'
    with open(output_file, 'w') as f:
        json.dump(valid_jobs, f, indent=2)
    
    print(f"✅ Saved to {output_file}")

#!/usr/bin/env python3
"""
FBeed Dashboard Generator
Generates index.html dashboard from feed metadata with HK timezone
"""

import json
import os
from datetime import datetime
from jinja2 import Template
import pytz


def load_metadata():
    """Load feed metadata from JSON"""
    metadata_path = 'metadata/feed-status.json'
    if not os.path.exists(metadata_path):
        return {'feeds': [], 'last_run': None}
    
    with open(metadata_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_hk_time(utc_time_str):
    """Convert UTC time string to Hong Kong timezone"""
    if not utc_time_str:
        return 'Never'
    
    try:
        # Parse ISO format UTC time
        utc_time = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
        
        # Convert to HK timezone
        hk_tz = pytz.timezone('Asia/Hong_Kong')
        hk_time = utc_time.astimezone(hk_tz)
        
        # Format as readable string
        return hk_time.strftime('%m/%d/%Y %I:%M %p HKT')
    except Exception as e:
        print(f"Error formatting time {utc_time_str}: {e}")
        return utc_time_str


def get_relative_time(utc_time_str):
    """Get relative time (e.g., '2 min ago')"""
    if not utc_time_str:
        return 'Never'
    
    try:
        utc_time = datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
        now = datetime.now(pytz.UTC)
        delta = now - utc_time
        
        seconds = delta.total_seconds()
        
        if seconds < 60:
            return f"{int(seconds)} sec ago"
        elif seconds < 3600:
            return f"{int(seconds / 60)} min ago"
        elif seconds < 86400:
            return f"{int(seconds / 3600)} hr ago"
        else:
            return f"{int(seconds / 86400)} days ago"
    except:
        return 'Unknown'


def get_status_icon(status):
    """Get status icon emoji"""
    status_map = {
        'success': '✅',
        'warning': '⚠️',
        'error': '❌'
    }
    return status_map.get(status, '❓')


def generate_dashboard():
    """Generate the HTML dashboard"""
    print("FBeed - Generating dashboard...")
    
    # Load metadata
    metadata = load_metadata()
    
    # Process feeds data for template
    feeds_data = []
    for feed in metadata.get('feeds', []):
        feeds_data.append({
            'title': feed.get('title', 'Untitled'),
            'fetchrss_url': feed.get('fetchrss_url', ''),
            'accumulated_url': feed.get('accumulated_url', ''),
            'last_updated': format_hk_time(feed.get('last_updated')),
            'relative_time': get_relative_time(feed.get('last_updated')),
            'total_posts': feed.get('total_posts', 0),
            'new_posts': feed.get('new_posts_this_run', 0),
            'status': feed.get('status', 'unknown'),
            'status_icon': get_status_icon(feed.get('status', 'unknown')),
            'description': feed.get('description', '')
        })
    
    # Last run time
    last_run = format_hk_time(metadata.get('last_run'))
    
    # Load HTML template
    template_path = 'template.html'
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    else:
        # Use inline template if file doesn't exist
        template_content = get_inline_template()
    
    # Render template
    template = Template(template_content)
    html_output = template.render(
        feeds=feeds_data,
        last_run=last_run,
        total_feeds=len(feeds_data),
        total_posts=sum(f['total_posts'] for f in feeds_data)
    )
    
    # Save to index.html
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print(f"✅ Dashboard generated: index.html")
    print(f"   Total feeds: {len(feeds_data)}")
    print(f"   Total posts: {sum(f['total_posts'] for f in feeds_data)}")
    print(f"   Last run: {last_run}")


def get_inline_template():
    """Fallback inline template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FBeed Dashboard</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>📋 FBeed Dashboard</h1>
            <p class="subtitle">Facebook Feed Accumulator</p>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{{ total_feeds }}</div>
                <div class="stat-label">Active Feeds</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ total_posts }}</div>
                <div class="stat-label">Total Posts</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ last_run }}</div>
                <div class="stat-label">Last Update</div>
            </div>
        </div>
        
        <div class="table-container">
            <table class="feed-table">
                <thead>
                    <tr>
                        <th>Feed Name</th>
                        <th>FetchRSS Source</th>
                        <th>Accumulated Feed</th>
                        <th>Last Updated</th>
                        <th>Posts</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for feed in feeds %}
                    <tr>
                        <td class="feed-title">{{ feed.title }}</td>
                        <td><a href="{{ feed.fetchrss_url }}" target="_blank" class="btn-link">Source →</a></td>
                        <td>
                            <button class="btn-copy" onclick="copyToClipboard('{{ feed.accumulated_url }}')">
                                📋 Copy RSS
                            </button>
                        </td>
                        <td class="time-cell">
                            <div class="relative-time">{{ feed.relative_time }}</div>
                            <div class="absolute-time">{{ feed.last_updated }}</div>
                        </td>
                        <td class="posts-count">{{ feed.total_posts }}</td>
                        <td class="status-cell">{{ feed.status_icon }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Updated every 15 minutes via GitHub Actions</p>
            <p>Powered by <a href="https://github.com/tommykhs/FBeed">FBeed</a></p>
        </footer>
    </div>
    
    <script>
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert('RSS URL copied to clipboard!');
            }).catch(err => {
                console.error('Failed to copy:', err);
            });
        }
    </script>
</body>
</html>"""


if __name__ == '__main__':
    generate_dashboard()

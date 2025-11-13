#!/usr/bin/env python3
"""Clean metadata to match config.yaml"""
import json
import yaml

# Load config
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Get all valid fetchrss URLs from config
valid_urls = {feed['fetchrss_url'] for feed in config['feeds']}

# Load metadata
with open('metadata/feed-status.json', 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# Filter feeds to keep only those in config
original_count = len(metadata['feeds'])
metadata['feeds'] = [
    feed for feed in metadata['feeds']
    if feed['fetchrss_url'] in valid_urls
]
cleaned_count = len(metadata['feeds'])

# Save cleaned metadata
with open('metadata/feed-status.json', 'w', encoding='utf-8') as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print(f"✅ Cleaned metadata: {original_count} → {cleaned_count} feeds")
print(f"   Removed: {original_count - cleaned_count} orphaned feeds")

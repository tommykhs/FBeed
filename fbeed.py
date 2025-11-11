#!/usr/bin/env python3
"""
FBeed - Facebook Feed Accumulator
Fetches FetchRSS feeds, accumulates posts, and generates metadata.
"""

import os
import json
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
import yaml
import requests
import feedparser
from xml.etree import ElementTree as ET
from xml.dom import minidom

# Hong Kong timezone (UTC+8)
HK_TZ = timezone(timedelta(hours=8))


def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def generate_slug(title):
    """Generate a URL-friendly slug from feed title"""
    # Convert to lowercase
    slug = title.lower()
    # Replace spaces with hyphens
    slug = slug.replace(' ', '-')
    # Remove special characters but keep Chinese characters and alphanumeric
    slug = re.sub(r'[^\w\s\u4e00-\u9fff-]', '', slug)
    # Remove extra hyphens
    slug = re.sub(r'-+', '-', slug)
    slug = slug.strip('-')
    return slug


def fetch_feed(url):
    """Fetch and parse RSS feed from FetchRSS"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        feed = feedparser.parse(response.content)
        return feed
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def load_existing_feed(feed_path):
    """Load existing accumulated feed if it exists"""
    if not os.path.exists(feed_path):
        return None
    
    try:
        tree = ET.parse(feed_path)
        root = tree.getroot()
        
        # Extract existing GUIDs
        existing_guids = set()
        channel = root.find('channel')
        if channel is not None:
            for item in channel.findall('item'):
                guid_elem = item.find('guid')
                if guid_elem is not None and guid_elem.text:
                    existing_guids.add(guid_elem.text)
        
        return {'tree': tree, 'root': root, 'guids': existing_guids}
    except Exception as e:
        print(f"Error loading existing feed {feed_path}: {e}")
        return None


def create_new_feed(feed_data):
    """Create a new RSS feed structure"""
    # Register namespace prefixes - ElementTree will add xmlns when needed
    ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
    ET.register_namespace('media', 'http://search.yahoo.com/mrss/')
    ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
    
    # Create RSS element with ONLY version - no manual xmlns
    rss = ET.Element('rss')
    rss.set('version', '2.0')
    
    channel = ET.SubElement(rss, 'channel')
    
    # Add channel metadata
    ET.SubElement(channel, 'title').text = feed_data.feed.get('title', 'Untitled Feed')
    ET.SubElement(channel, 'description').text = feed_data.feed.get('description', '')
    ET.SubElement(channel, 'link').text = feed_data.feed.get('link', '')
    ET.SubElement(channel, 'pubDate').text = datetime.now(HK_TZ).strftime('%a, %d %b %Y %H:%M:%S +0800')
    
    # Add Facebook icon as feed image
    image = ET.SubElement(channel, 'image')
    ET.SubElement(image, 'url').text = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHZpZXdCb3g9JzAgMCAyNCAyNCc+PHBhdGggZmlsbD0nIzE4NzdmMicgZD0nTTI0IDEyLjA3M2MwLTYuNjI3LTUuMzczLTEyLTEyLTEycy0xMiA1LjM3My0xMiAxMmMwIDUuOTkgNC4zODggMTAuOTU0IDEwLjEyNSAxMS44NTR2LTguMzg1SDcuMDc4di0zLjQ3aDMuMDQ3VjkuNDNjMC0zLjAwNyAxLjc5Mi00LjY2OSA0LjUzMy00LjY2OSAxLjMxMiAwIDIuNjg2LjIzNSAyLjY4Ni4yMzV2Mi45NTNIMTUuODNjLTEuNDkxIDAtMS45NTYuOTI1LTEuOTU2IDEuODc0djIuMjVoMy4zMjhsLS41MzIgMy40N2gtMi43OTZ2OC4zODVDMTkuNjEyIDIzLjAyNyAyNCAxOC4wNjIgMjQgMTIuMDczeicvPjwvc3ZnPg=='
    ET.SubElement(image, 'title').text = feed_data.feed.get('title', 'Untitled Feed')
    ET.SubElement(image, 'link').text = feed_data.feed.get('link', '')
    
    # Add generator
    ET.SubElement(channel, 'generator').text = 'FBeed - Facebook Feed Accumulator'
    
    return ET.ElementTree(rss)


def parse_rfc822_date(date_str):
    """Parse RFC 822 date string to datetime for sorting"""
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(date_str)
    except Exception:
        # If parsing fails, return a very old date so it goes to the end
        return datetime(1970, 1, 1, tzinfo=timezone.utc)


def sort_feed_items(channel):
    """Sort all items in the feed by pubDate (newest first)"""
    # Get all item elements
    items = channel.findall('item')
    
    if not items:
        return
    
    # Extract items with their pubDate for sorting
    items_with_dates = []
    for item in items:
        pubdate_elem = item.find('pubDate')
        if pubdate_elem is not None and pubdate_elem.text:
            pub_date = parse_rfc822_date(pubdate_elem.text)
        else:
            pub_date = datetime(1970, 1, 1, tzinfo=timezone.utc)
        items_with_dates.append((pub_date, item))
    
    # Sort by date (newest first)
    items_with_dates.sort(key=lambda x: x[0], reverse=True)
    
    # Remove all items from channel
    for item in items:
        channel.remove(item)
    
    # Re-add items in sorted order
    for _, item in items_with_dates:
        channel.append(item)


def add_items_to_feed(tree, feed_data, existing_guids):
    """Add new items from feed_data to the XML tree"""
    root = tree.getroot()
    channel = root.find('channel')
    
    new_items_count = 0
    
    # Get all items from the fetched feed
    for entry in feed_data.entries:
        guid = entry.get('id', entry.get('link', ''))
        
        # Skip if already exists
        if guid in existing_guids:
            continue
        
        # Create new item element
        item = ET.Element('item')
        
        # Title
        if 'title' in entry:
            ET.SubElement(item, 'title').text = entry.title
        
        # Link
        if 'link' in entry:
            ET.SubElement(item, 'link').text = entry.link
        
        # Description
        if 'description' in entry:
            desc = ET.SubElement(item, 'description')
            desc.text = entry.description
        elif 'summary' in entry:
            desc = ET.SubElement(item, 'description')
            desc.text = entry.summary
        
        # Author/Creator
        if 'author' in entry:
            ET.SubElement(item, '{http://purl.org/dc/elements/1.1/}creator').text = entry.author
        
        # PubDate
        if 'published' in entry:
            ET.SubElement(item, 'pubDate').text = entry.published
        elif 'updated' in entry:
            ET.SubElement(item, 'pubDate').text = entry.updated
        
        # Media content
        if 'media_content' in entry and entry.media_content:
            media = entry.media_content[0]
            media_elem = ET.SubElement(item, '{http://search.yahoo.com/mrss/}content')
            if 'url' in media:
                media_elem.set('url', media['url'])
            if 'medium' in media:
                media_elem.set('medium', media['medium'])
        
        # GUID
        guid_elem = ET.SubElement(item, 'guid')
        guid_elem.set('isPermaLink', 'false')
        guid_elem.text = guid
        
        # Add to channel (will be sorted later)
        channel.append(item)
        existing_guids.add(guid)
        new_items_count += 1
    
    # Sort all items by pubDate (newest first)
    sort_feed_items(channel)
    
    # Update channel pubDate
    pubdate_elem = channel.find('pubDate')
    if pubdate_elem is not None:
        pubdate_elem.text = datetime.now(HK_TZ).strftime('%a, %d %b %Y %H:%M:%S +0800')
    
    return new_items_count


def prettify_xml(elem):
    """Return a pretty-printed XML string with XSL stylesheet reference"""
    rough_string = ET.tostring(elem, encoding='utf-8', xml_declaration=True)
    xml_str = rough_string.decode('utf-8')
    
    # Add XSL stylesheet processing instruction after XML declaration
    xml_lines = xml_str.split('\n')
    if xml_lines[0].startswith('<?xml'):
        xml_lines.insert(1, '<?xml-stylesheet type="text/xsl" href="/FBeed/feed-style.xsl"?>')
        xml_str = '\n'.join(xml_lines)
    
    return xml_str


def save_feed(tree, feed_path):
    """Save the feed to file"""
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(feed_path), exist_ok=True)
    
    # Pretty print and save
    xml_string = prettify_xml(tree.getroot())
    
    with open(feed_path, 'w', encoding='utf-8') as f:
        f.write(xml_string)


def update_metadata(metadata, feed_info):
    """Update metadata with feed information"""
    # Find existing feed or create new entry
    existing_feed = None
    for feed in metadata.get('feeds', []):
        if feed['fetchrss_url'] == feed_info['fetchrss_url']:
            existing_feed = feed
            break
    
    if existing_feed:
        # Update existing
        existing_feed.update(feed_info)
    else:
        # Add new
        if 'feeds' not in metadata:
            metadata['feeds'] = []
        metadata['feeds'].append(feed_info)
    
    metadata['last_run'] = datetime.now(HK_TZ).isoformat()


def main():
    """Main execution function"""
    print("FBeed - Starting feed accumulation...")
    
    # Load configuration
    config = load_config()
    
    # Load or create metadata
    metadata_path = 'metadata/feed-status.json'
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        metadata = {'feeds': [], 'last_run': None}
    
    # Process each feed
    for feed_config in config['feeds']:
        fetchrss_url = feed_config['fetchrss_url']
        print(f"\nProcessing: {fetchrss_url}")
        
        # Fetch feed
        feed_data = fetch_feed(fetchrss_url)
        if not feed_data or not feed_data.entries:
            print(f"  ❌ Failed to fetch or empty feed")
            continue
        
        # Extract metadata
        feed_title = feed_data.feed.get('title', 'Untitled Feed')
        feed_description = feed_data.feed.get('description', '')
        feed_link = feed_data.feed.get('link', '')
        slug = generate_slug(feed_title)
        
        print(f"  Feed: {feed_title}")
        print(f"  Slug: {slug}")
        
        # Load existing or create new feed
        feed_path = f'feeds/{slug}.xml'
        existing = load_existing_feed(feed_path)
        
        if existing:
            tree = existing['tree']
            existing_guids = existing['guids']
            print(f"  Loaded existing feed with {len(existing_guids)} posts")
        else:
            tree = create_new_feed(feed_data)
            existing_guids = set()
            print(f"  Creating new feed")
        
        # Add new items
        new_items_count = add_items_to_feed(tree, feed_data, existing_guids)
        print(f"  Added {new_items_count} new posts")
        
        # Save feed
        save_feed(tree, feed_path)
        print(f"  ✅ Saved to {feed_path}")
        
        # Update metadata
        feed_info = {
            'title': feed_title,
            'slug': slug,
            'fetchrss_url': fetchrss_url,
            'accumulated_url': f'https://tommykhs.github.io/FBeed/feeds/{slug}.xml',
            'description': feed_description,
            'link': feed_link,
            'last_updated': datetime.now(HK_TZ).isoformat(),
            'status': 'success',
            'total_posts': len(existing_guids),
            'new_posts_this_run': new_items_count
        }
        update_metadata(metadata, feed_info)
    
    # Save metadata
    os.makedirs('metadata', exist_ok=True)
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Feed accumulation complete!")
    print(f"Metadata saved to {metadata_path}")


if __name__ == '__main__':
    main()

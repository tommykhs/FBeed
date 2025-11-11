# 📋 FBeed - Facebook Feed Accumulator

**Automated Facebook feed accumulator that fetches FetchRSS feeds, accumulates posts, and generates a beautiful dashboard.**

🔗 **Live Dashboard**: [https://tommykhs.github.io/FBeed](https://tommykhs.github.io/FBeed)

## ✨ Features

- 🤖 **Fully Automated** - Runs every 15 minutes via GitHub Actions
- 🔄 **Auto-Accumulation** - Never lose posts when they fall off FetchRSS
- 📊 **Beautiful Dashboard** - Modern, responsive UI with real-time stats
- 🌏 **HK Timezone** - Last update times displayed in Hong Kong timezone
- 📋 **One-Click Copy** - Copy accumulated RSS URLs to clipboard
- 🎯 **Zero Configuration** - Just paste FetchRSS URLs, everything else is automatic
- 🆓 **Free Forever** - Powered by GitHub Pages and Actions

## 🚀 Quick Start

### 1. Fork or Clone This Repository

```bash
git clone https://github.com/tommykhs/FBeed.git
cd FBeed
```

### 2. Add Your FetchRSS URLs

Edit `config.yaml`:

```yaml
feeds:
  - fetchrss_url: "https://fetchrss.com/feed/YOUR_FEED_1.rss"
  - fetchrss_url: "https://fetchrss.com/feed/YOUR_FEED_2.rss"
  - fetchrss_url: "https://fetchrss.com/feed/YOUR_FEED_3.rss"

settings:
  update_interval_minutes: 15
```

**That's it!** No manual naming needed - feed names are extracted automatically from RSS.

### 3. Enable GitHub Pages

1. Go to your repository **Settings**
2. Navigate to **Pages**
3. Under "Source", select **Deploy from a branch**
4. Select branch: **main** and folder: **/ (root)**
5. Click **Save**

### 4. Enable GitHub Actions

1. Go to **Actions** tab
2. Click **"I understand my workflows, go ahead and enable them"**
3. The workflow will run automatically every 15 minutes

### 5. Manual First Run (Optional)

To trigger the first run immediately:

1. Go to **Actions** tab
2. Click on **"Update FBeed Feeds"** workflow
3. Click **"Run workflow"** → **"Run workflow"**

## 📁 Project Structure

```
FBeed/
├── .github/
│   └── workflows/
│       └── update-feeds.yml          # GitHub Actions workflow (15-min schedule)
├── feeds/                            # Accumulated RSS feeds (auto-generated)
├── metadata/
│   └── feed-status.json              # Feed metadata (auto-generated)
├── config.yaml                       # Your FetchRSS URLs (edit this!)
├── fbeed.py                          # Main feed accumulator script
├── generate_index.py                 # Dashboard generator
├── template.html                     # Dashboard HTML template
├── style.css                         # Dashboard styling
├── index.html                        # Generated dashboard (auto-generated)
├── requirements.txt                  # Python dependencies
└── README.md                         # This file
```

## 🔧 How It Works

### Every 15 Minutes:

1. **GitHub Actions triggers** the workflow
2. **Fetch FetchRSS feeds** from your URLs in `config.yaml`
3. **Extract metadata** automatically:
   - Feed title from `<channel><title>`
   - Feed description from `<channel><description>`
   - Generate slug from title (e.g., "Fomo研究院 on Facebook" → "fomo研究院-on-facebook")
4. **Load existing accumulated feed** (if exists)
5. **Compare GUIDs** to find new posts
6. **Add new posts** to accumulated feed (prepend to maintain chronological order)
7. **Save accumulated feed** to `feeds/{slug}.xml`
8. **Update metadata** JSON with stats
9. **Generate dashboard** HTML with HK timezone
10. **Git commit** (only if changes detected)
11. **Push to GitHub** → GitHub Pages serves the update

## 📊 Dashboard Features

The auto-generated dashboard displays:

- **Feed Name** - Automatically extracted from RSS
- **FetchRSS Source** - Link to original FetchRSS feed
- **Copy RSS Button** - One-click copy of accumulated feed URL
- **Last Updated** - Relative time (e.g., "2 min ago") + absolute HK time
- **Post Count** - Total accumulated posts
- **Status** - ✅ success, ⚠️ warning, ❌ error

### Stats Cards

- **Active Feeds** - Number of feeds being tracked
- **Total Posts** - Sum of all accumulated posts
- **Last Update** - When the system last ran (HK time)

## ⚙️ Configuration

### Update Interval

Default: **15 minutes**

To change, edit `.github/workflows/update-feeds.yml`:

```yaml
schedule:
  - cron: '*/15 * * * *'  # Every 15 minutes
  # - cron: '*/30 * * * *'  # Every 30 minutes
  # - cron: '0 * * * *'     # Every hour
```

### Accumulated Feed URLs

Your accumulated feeds will be available at:

```
https://YOUR_USERNAME.github.io/FBeed/feeds/{slug}.xml
```

For example:
```
https://tommykhs.github.io/FBeed/feeds/fomo研究院-on-facebook.xml
```

## 🛠️ Local Development

### Requirements

- Python 3.11+
- pip

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run feed accumulator
python fbeed.py

# Generate dashboard
python generate_index.py

# Open dashboard
open index.html
```

## 📝 Adding/Removing Feeds

### To Add a New Feed:

1. Go to your repository on GitHub
2. Edit `config.yaml`
3. Add new line:
   ```yaml
   - fetchrss_url: "https://fetchrss.com/feed/NEW_FEED.rss"
   ```
4. Commit changes
5. Wait 15 minutes (or manually trigger workflow)
6. Feed appears on dashboard automatically!

### To Remove a Feed:

1. Edit `config.yaml`
2. Delete the URL line
3. Commit changes
4. Feed stops updating (existing XML file remains unless manually deleted)

## 🔐 Security

- No API keys or tokens required
- Runs on GitHub's infrastructure
- All code is open source and auditable
- Uses official GitHub Actions

## 📈 Usage Limits

- **GitHub Actions**: Unlimited for public repositories
- **GitHub Pages**: 100GB bandwidth/month (soft limit)
- **FetchRSS**: 4 requests/hour per feed (we run every 15 min = 4/hour, perfect!)

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🙏 Acknowledgments

- **FetchRSS** - For providing Facebook RSS feeds
- **GitHub** - For free hosting and automation
- **feedparser** - For RSS parsing
- **Jinja2** - For template rendering

## 📞 Support

If you encounter issues:

1. Check the **Actions** tab for workflow logs
2. Verify your FetchRSS URLs are valid
3. Ensure GitHub Pages is enabled
4. Open an issue on GitHub

---

**Built with ❤️ by [Tommy](https://github.com/tommykhs)**

**Last Updated**: November 11, 2025

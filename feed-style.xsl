<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" 
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:media="http://search.yahoo.com/mrss/">
    
    <xsl:output method="html" encoding="UTF-8" indent="yes"/>
    
    <xsl:template match="/">
        <html lang="en">
        <head>
            <meta charset="UTF-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
            <title><xsl:value-of select="rss/channel/title"/> - RSS Feed</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                :root {
                    --primary-color: #1877f2;
                    --bg-color: #f8fafc;
                    --card-bg: #ffffff;
                    --text-primary: #1e293b;
                    --text-secondary: #64748b;
                    --border-color: #e2e8f0;
                    --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
                }
                
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background-color: var(--bg-color);
                    color: var(--text-primary);
                    line-height: 1.6;
                    padding: 16px;
                }
                
                .container {
                    max-width: 900px;
                    margin: 0 auto;
                }
                
                .header {
                    background: var(--card-bg);
                    padding: 24px;
                    border-radius: 8px;
                    box-shadow: var(--shadow);
                    margin-bottom: 24px;
                    text-align: center;
                }
                
                .header h1 {
                    font-size: 1.75rem;
                    font-weight: 600;
                    color: var(--primary-color);
                    margin-bottom: 8px;
                }
                
                .header .description {
                    color: var(--text-secondary);
                    font-size: 0.875rem;
                    margin-bottom: 12px;
                }
                
                .feed-info {
                    display: inline-block;
                    background: var(--bg-color);
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-size: 0.75rem;
                    color: var(--text-secondary);
                    margin-top: 8px;
                }
                
                .items {
                    display: flex;
                    flex-direction: column;
                    gap: 16px;
                }
                
                .item {
                    background: var(--card-bg);
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: var(--shadow);
                    border-left: 4px solid var(--primary-color);
                }
                
                .item-title {
                    font-size: 1.25rem;
                    font-weight: 600;
                    margin-bottom: 8px;
                }
                
                .item-title a {
                    color: var(--text-primary);
                    text-decoration: none;
                }
                
                .item-title a:hover {
                    color: var(--primary-color);
                    text-decoration: underline;
                }
                
                .item-meta {
                    display: flex;
                    gap: 16px;
                    margin-bottom: 12px;
                    flex-wrap: wrap;
                }
                
                .item-date,
                .item-author {
                    font-size: 0.8125rem;
                    color: var(--text-secondary);
                }
                
                .item-description {
                    color: var(--text-primary);
                    font-size: 0.9375rem;
                    line-height: 1.6;
                }
                
                .item-description img {
                    max-width: 100%;
                    height: auto;
                    border-radius: 4px;
                    margin: 8px 0;
                }
                
                .footer {
                    text-align: center;
                    padding: 24px;
                    color: var(--text-secondary);
                    font-size: 0.75rem;
                }
                
                @media (max-width: 768px) {
                    body {
                        padding: 12px;
                    }
                    
                    .header {
                        padding: 16px;
                    }
                    
                    .header h1 {
                        font-size: 1.25rem;
                    }
                    
                    .item {
                        padding: 16px;
                    }
                    
                    .item-title {
                        font-size: 1.125rem;
                    }
                    
                    .item-meta {
                        gap: 12px;
                    }
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1><xsl:value-of select="rss/channel/title"/></h1>
                    <div class="description">
                        <xsl:value-of select="rss/channel/description"/>
                    </div>
                    <div class="feed-info">
                        RSS Feed • <xsl:value-of select="count(rss/channel/item)"/> Posts
                    </div>
                </div>
                
                <div class="items">
                    <xsl:for-each select="rss/channel/item">
                        <div class="item">
                            <div class="item-title">
                                <a href="{link}" target="_blank">
                                    <xsl:value-of select="title"/>
                                </a>
                            </div>
                            <div class="item-meta">
                                <xsl:if test="pubDate">
                                    <span class="item-date">
                                        📅 <xsl:value-of select="pubDate"/>
                                    </span>
                                </xsl:if>
                                <xsl:if test="dc:creator">
                                    <span class="item-author">
                                        ✍️ <xsl:value-of select="dc:creator"/>
                                    </span>
                                </xsl:if>
                            </div>
                            <div class="item-description">
                                <xsl:value-of select="description" disable-output-escaping="yes"/>
                            </div>
                        </div>
                    </xsl:for-each>
                </div>
                
                <div class="footer">
                    <p>Generated by FBeed - Facebook Feed Accumulator</p>
                    <p>Subscribe to this feed in your RSS reader</p>
                </div>
            </div>
        </body>
        </html>
    </xsl:template>
</xsl:stylesheet>

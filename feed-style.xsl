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
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"/>
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
            <script>
                // Convert UTC dates to HK timezone (UTC+8)
                function convertToHKTime() {
                    const dateElements = document.querySelectorAll('.item-date');
                    dateElements.forEach(element => {
                        const dateText = element.textContent.trim();
                        // Extract date string after emoji
                        const dateString = dateText.replace('📅 ', '');
                        
                        try {
                            // Parse the RFC 822 date format
                            const date = new Date(dateString);
                            
                            if (!isNaN(date.getTime())) {
                                // Convert to HK timezone (UTC+8)
                                const options = {
                                    timeZone: 'Asia/Hong_Kong',
                                    weekday: 'short',
                                    year: 'numeric',
                                    month: 'short',
                                    day: '2-digit',
                                    hour: '2-digit',
                                    minute: '2-digit',
                                    second: '2-digit',
                                    hour12: false
                                };
                                
                                const formatter = new Intl.DateTimeFormat('en-US', options);
                                const parts = formatter.formatToParts(date);
                                
                                // Build formatted string
                                const formatted = `${parts.find(p => p.type === 'weekday').value}, ` +
                                    `${parts.find(p => p.type === 'day').value} ` +
                                    `${parts.find(p => p.type === 'month').value} ` +
                                    `${parts.find(p => p.type === 'year').value} ` +
                                    `${parts.find(p => p.type === 'hour').value}:` +
                                    `${parts.find(p => p.type === 'minute').value}:` +
                                    `${parts.find(p => p.type === 'second').value} +0800`;
                                
                                element.textContent = `📅 ${formatted}`;
                                element.classList.add('converted');
                            }
                        } catch (e) {
                            // Keep original if parsing fails
                            console.error('Date parsing error:', e);
                        }
                    });
                }
                
                // Pagination
                const ITEMS_PER_PAGE = 20;
                let currentPage = 1;
                let totalItems = 0;
                
                function initPagination() {
                    const items = document.querySelectorAll('.item');
                    totalItems = items.length;
                    
                    if (totalItems <= ITEMS_PER_PAGE) {
                        return; // No pagination needed
                    }
                    
                    showPage(1);
                    renderPagination();
                }
                
                function showPage(page) {
                    currentPage = page;
                    const items = document.querySelectorAll('.item');
                    const start = (page - 1) * ITEMS_PER_PAGE;
                    const end = start + ITEMS_PER_PAGE;
                    
                    items.forEach((item, index) => {
                        if (index >= start && index < end) {
                            item.style.display = 'block';
                        } else {
                            item.style.display = 'none';
                        }
                    });
                    
                    // Scroll to top
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                    renderPagination();
                }
                
                function renderPagination() {
                    const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);
                    const paginationContainer = document.getElementById('pagination');
                    
                    if (!paginationContainer || totalPages <= 1) {
                        return;
                    }
                    
                    let html = '<ul class="pagination justify-content-center">';
                    
                    // Previous button
                    html += `<li class="page-item ${currentPage === 1 ? 'disabled' : ''}">`;
                    html += `<a class="page-link" href="#" onclick="showPage(${currentPage - 1}); return false;">Previous</a>`;
                    html += '</li>';
                    
                    // Page numbers
                    const maxVisiblePages = 5;
                    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
                    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
                    
                    if (endPage - startPage < maxVisiblePages - 1) {
                        startPage = Math.max(1, endPage - maxVisiblePages + 1);
                    }
                    
                    if (startPage > 1) {
                        html += `<li class="page-item"><a class="page-link" href="#" onclick="showPage(1); return false;">1</a></li>`;
                        if (startPage > 2) {
                            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
                        }
                    }
                    
                    for (let i = startPage; i <= endPage; i++) {
                        html += `<li class="page-item ${i === currentPage ? 'active' : ''}">`;
                        html += `<a class="page-link" href="#" onclick="showPage(${i}); return false;">${i}</a>`;
                        html += '</li>';
                    }
                    
                    if (endPage < totalPages) {
                        if (endPage < totalPages - 1) {
                            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
                        }
                        html += `<li class="page-item"><a class="page-link" href="#" onclick="showPage(${totalPages}); return false;">${totalPages}</a></li>`;
                    }
                    
                    // Next button
                    html += `<li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">`;
                    html += `<a class="page-link" href="#" onclick="showPage(${currentPage + 1}); return false;">Next</a>`;
                    html += '</li>';
                    
                    html += '</ul>';
                    paginationContainer.innerHTML = html;
                }
                
                // Run on DOM load
                document.addEventListener('DOMContentLoaded', function() {
                    convertToHKTime();
                    initPagination();
                });
            </script>
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
                
                <div id="pagination" class="my-4"></div>
                
                <div class="footer">
                    <p>Generated by FBeed - Facebook Feed Accumulator</p>
                    <p>Subscribe to this feed in your RSS reader</p>
                </div>
            </div>
        </body>
        </html>
    </xsl:template>
</xsl:stylesheet>

import requests
import feedparser
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime, timedelta
import sqlite3
import schedule
import re

DATABASE_FILE = "news_data.db"
NEWS_SOURCES = [
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "type": "rss",
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
        "type": "rss",
    },
    {
        "name": "Simon Willison's Blog",
        "url": "https://simonwillison.net/atom/everything/",
        "type": "rss",
    },
    {
        "name": "One Useful Thing",
        "url": "https://www.oneusefulthing.org/feed",
        "type": "rss",
    },
    {
        "name": "LinkedIn",
        "url": "https://www.linkedin.com/",
        "type": "scrape",
        "scrape_function": "scrape_linkedin",
    },
]

def create_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            link TEXT,
            published TEXT,
            content TEXT,
            read INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def get_article_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        # Adjust the selectors based on the website's structure
        article_text_parts = soup.find_all("p")  # This is a common selector, adjust as needed
        full_text = "\n".join(part.get_text() for part in article_text_parts)

        # Remove newline and other non wanted characters
        full_text = re.sub(r'\n\s*\n', '\n', full_text)
        return full_text.strip()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching article text: {e}")
        return None

def scrape_simon_willison_post(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        content_div = soup.find("div", class_="article-body")
        if content_div:
            full_text = content_div.get_text(separator="\n")
            #Remove newlines
            full_text = re.sub(r'\n\s*\n', '\n', full_text)
            return full_text.strip()
        else:
            return get_article_text(url)
    except Exception as e:
        print(f"Error scraping Simon Willison's blog: {e}")
        return None

def scrape_oneusefulthing_post(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        content_div = soup.find("div", class_="post-body")
        if content_div:
            full_text = content_div.get_text(separator="\n")
            #Remove newlines
            full_text = re.sub(r'\n\s*\n', '\n', full_text)
            return full_text.strip()
        else:
            return get_article_text(url)
    except Exception as e:
        print(f"Error scraping One Useful Thing: {e}")
        return None

def scrape_linkedin(url):
    # This is a placeholder, LinkedIn scraping is challenging.
    # You'll likely need a specialized library for this, or use an API if available.
    # Consider using Selenium to automate browser interactions.
    # Or use LinkedIn API if you have a developper account.
    print("LinkedIn scraping placeholder. Complex authentication required.")
    return f"Scraped from LinkedIn (placeholder): {url}"

def fetch_rss_news(source):
    """Fetches news from an RSS feed."""
    try:
        feed = feedparser.parse(source["url"])
        if feed.bozo:
            print(f"Error parsing RSS feed for {source['name']}: {feed.bozo_exception}")
            return []
        news_items = []
        for entry in feed.entries:
            published = entry.get("published")
            if not published:
                # If no publication date is found, we don't add to the news feed.
                continue

            if source['name'] == "Simon Willison's Blog":
                content = scrape_simon_willison_post(entry.link)
            elif source['name'] == "One Useful Thing":
                content = scrape_oneusefulthing_post(entry.link)
            else:
                if 'content' in entry:
                    content = entry.content[0].value
                elif 'summary' in entry:
                    content = entry.summary
                else:
                    content = ''

            news_items.append({
                "source": source["name"],
                "title": entry.title,
                "link": entry.link,
                "published": published,
                "content": content,
            })
        return news_items
    except Exception as e:
        print(f"Error fetching RSS feed for {source['name']}: {e}")
        return []

def fetch_news():
    """Fetches news from all sources."""
    all_news = []
    for source in NEWS_SOURCES:
        if source["type"] == "rss":
            all_news.extend(fetch_rss_news(source))
        elif source["type"] == "scrape":
            if source.get('scrape_function'):
                scrape_func = globals()[source.get('scrape_function')]
                #Get the new posts from the website
                for _ in range(2):
                    url = source.get('url')
                    #This will call the function defined in scrape_function
                    content = scrape_func(url)
                    if content:
                        all_news.append({
                            "source": source["name"],
                            "title": f"{source['name']} post",
                            "link": url,
                            "published": datetime.now().strftime('%a, %d %b %Y %H:%M:%S %Z'),
                            "content": content,
                        })
    return all_news

def insert_news_to_db(news_list):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    for news in news_list:
        try:
            # Check if the news already exists based on the link
            cursor.execute("SELECT id FROM news WHERE link=?", (news['link'],))
            existing_news = cursor.fetchone()

            if not existing_news:
                cursor.execute(
                    "INSERT INTO news (source, title, link, published, content) VALUES (?, ?, ?, ?, ?)",
                    (news['source'], news['title'], news['link'], news['published'], news['content'])
                )
        except Exception as e:
            print(f"Error inserting news into database: {e}")
    conn.commit()
    conn.close()

def delete_old_news():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    two_days_ago = datetime.now() - timedelta(days=2)
    formatted_date = two_days_ago.strftime('%a, %d %b %Y %H:%M:%S %Z')

    cursor.execute("DELETE FROM news WHERE published < ?", (formatted_date,))
    conn.commit()
    conn.close()
    
def get_news_from_db(since_hours = 48):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    time_threshold = datetime.now() - timedelta(hours=since_hours)
    time_threshold_str = time_threshold.strftime('%a, %d %b %Y %H:%M:%S %Z')

    cursor.execute("SELECT id, source, title, link, published, content, read FROM news WHERE published >= ? ORDER BY published DESC", (time_threshold_str,))
    news_items = []
    for row in cursor.fetchall():
        news_items.append({
            'id': row[0],
            'source': row[1],
            'title': row[2],
            'link': row[3],
            'published': row[4],
            'content': row[5],
            'read': row[6]
        })
    conn.close()
    return news_items

def update_news_read_status(news_id, read_status):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE news SET read = ? WHERE id = ?", (read_status, news_id))
    conn.commit()
    conn.close()

def update_news():
    print("Updating news...")
    new_news = fetch_news()
    insert_news_to_db(new_news)
    delete_old_news()
    print("News updated.")

def main():
    create_database()
    update_news()
    schedule.every().hour.do(update_news)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()

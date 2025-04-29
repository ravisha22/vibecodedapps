from flask import Flask, jsonify, render_template
import feedparser

app = Flask(__name__)

RSS_FEEDS = [
    'https://machinelearningmastery.com/blog/feed/',
    'https://marktechpost.com/feed/',
    'https://bair.berkeley.edu/blog/feed.xml',
    'https://news.mit.edu/rss/topic/artificial-intelligence',
    'https://techcrunch.com/feed/',
    'https://www.theverge.com/rss/index.xml',
    'https://www.wired.com/feed/rss',
    'https://mashable.com/feeds/rss/all'
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_news')
def get_news():
    news_items = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]:  # Get the latest 5 entries from each feed
            news_items.append({
                'title': entry.title,
                'description': entry.description,
                'link': entry.link
            })
    return jsonify(news_items)

if __name__ == '__main__':
    app.run(debug=True)

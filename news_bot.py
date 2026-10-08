import os
import feedparser
import requests

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHANNEL = os.environ["TELEGRAM_CHANNEL"]

RSS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/rss",
]

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": TELEGRAM_CHANNEL,
        "text": text,
        "disable_web_page_preview": False
    })

for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)

    if feed.entries:
        article = feed.entries[0]

        title = article.get("title", "")
        link = article.get("link", "")

        message = f"📰 {title}\n\n🔗 {link}"

        send_to_telegram(message)

import os
import json
import feedparser
import requests

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHANNEL = os.environ["TELEGRAM_CHANNEL"]

RSS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/rss",
]

SENT_FILE = "sent_articles.json"

if os.path.exists(SENT_FILE):
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        sent_articles = set(json.load(f))
else:
    sent_articles = set()

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHANNEL,
            "text": text,
            "disable_web_page_preview": False
        }
    )
    return response.ok

new_articles = []

for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)

    for article in feed.entries[:5]:
        title = article.get("title", "").strip()
        link = article.get("link", "").strip()

        if not title or not link:
            continue

        if link in sent_articles:
            continue

        message = f"📰 {title}\n\n🔗 {link}"

        if send_to_telegram(message):
            sent_articles.add(link)
            new_articles.append(link)

with open(SENT_FILE, "w", encoding="utf-8") as f:
    json.dump(list(sent_articles)[-500:], f, ensure_ascii=False, indent=2)

print(f"New articles sent: {len(new_articles)}")

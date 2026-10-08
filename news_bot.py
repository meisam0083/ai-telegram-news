import os
import json
import feedparser
import requests

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHANNEL = os.environ["TELEGRAM_CHANNEL"]

RSS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/rss/",
]

SENT_FILE = "sent_articles.json"

# Load previously sent articles
try:
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        sent_articles = set(json.load(f))
except:
    sent_articles = set()


def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    response = requests.post(
        url,
        data={
            "chat_id": TELEGRAM_CHANNEL,
            "text": text,
            "disable_web_page_preview": False
        },
        timeout=30
    )

    return response.ok


# Find only ONE new article
article_to_send = None

for feed_url in RSS_FEEDS:
    feed = feedparser.parse(feed_url)

    for article in feed.entries:
        title = article.get("title", "").strip()
        link = article.get("link", "").strip()

        if not title or not link:
            continue

        if link in sent_articles:
            continue

        article_to_send = {
            "title": title,
            "link": link
        }
        break

    if article_to_send:
        break


# Send only one article
if article_to_send:

    message = (
        f"📰 {article_to_send['title']}\n\n"
        f"🔗 {article_to_send['link']}"
    )

    if send_to_telegram(message):

        sent_articles.add(article_to_send["link"])

        # Keep only the latest 500 links
        sent_articles = set(list(sent_articles)[-500:])

        with open(SENT_FILE, "w", encoding="utf-8") as f:
            json.dump(
                list(sent_articles),
                f,
                ensure_ascii=False,
                indent=2
            )

        print("✅ One new article sent.")

    else:
        print("❌ Telegram sending failed.")

else:
    print("ℹ️ No new article found.")

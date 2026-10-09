import os
import json
import requests
import feedparser
import html

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHANNEL = os.environ["TELEGRAM_CHANNEL"]
GEMINI_KEY = os.environ["GEMINI_API_KEY"]

SENT_FILE = "sent_articles.json"

RSS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/rss/",
]

def load_sent():
    try:
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_sent(sent):
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(sent)[-500:], f, ensure_ascii=False, indent=2)

def summarize(title, description):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash:generateContent"
        f"?key={GEMINI_KEY}"
    )

    prompt = f"""
این خبر فناوری را به فارسی روان و دقیق بازنویسی کن.
یک تیتر جذاب و خلاصه‌ای حدود ۶۰ تا ۱۰۰ کلمه بنویس.
چیزی از خودت اختراع نکن.
فقط متن نهایی فارسی را برگردان.

عنوان: {title}
متن خبر: {description}
"""
    response = requests.post(
        url,
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=60
    )
    response.raise_for_status()
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"].strip()

def send_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    response = requests.post(
        url,
        data={
            "chat_id": CHANNEL,
            "text": message,
            "disable_web_page_preview": False
        },
        timeout=30
    )
    response.raise_for_status()

def main():
    sent = load_sent()
    article = None

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for item in feed.entries:
            link = item.get("link", "").strip()
            title = html.unescape(item.get("title", "").strip())
            description = html.unescape(
                item.get("summary", item.get("description", "")).strip()
            )

            if link and title and link not in sent:
                article = (title, description, link)
                break

        if article:
            break

    if not article:
        print("خبر جدیدی پیدا نشد.")
        return

    title, description, link = article
    print("در حال خلاصه‌سازی خبر:", title)

    summary = summarize(title, description)
    message = f"🤖 {summary}\n\n🔗 منبع: {link}"
    send_message(message)

    sent.add(link)
    save_sent(sent)
    print("خبر با موفقیت ارسال شد.")

if __name__ == "__main__":
    main()

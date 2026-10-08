import os
import json
import feedparser
import requests
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHANNEL = os.environ["TELEGRAM_CHANNEL"]

MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"

RSS_FEEDS = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://www.wired.com/feed/rss/",
]

SENT_FILE = "sent_articles.json"

try:
    with open(SENT_FILE, "r", encoding="utf-8") as f:
        sent_articles = set(json.load(f))
except:
    sent_articles = set()


print("Loading AI model...")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float32
)

print("AI model loaded.")


def summarize_persian(title, description):
    prompt = f"""
این خبر تکنولوژی را به فارسی روان و کوتاه خلاصه کن.

عنوان خبر:
{title}

متن خبر:
{description}

قوانین:
- یک تیتر فارسی جذاب بنویس.
- خلاصه بین 60 تا 100 کلمه باشد.
- اطلاعاتی که در متن نیست اختراع نکن.
- لحن خبری و ساده باشد.
- خروجی فقط متن فارسی باشد.
"""

    messages = [
        {"role": "system", "content": "تو یک سردبیر حرفه‌ای اخبار تکنولوژی هستی."},
        {"role": "user", "content": prompt}
    ]

    text = tokenizer

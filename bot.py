import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "schedule"])

import os
import time
import json
import schedule
import requests
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================
TELEGRAM_BOT_TOKEN = "8705818169:AAGjQkrty6hRyuOxNW_ivcBwildjjA3DLR8"
GROQ_API_KEY = "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"
OWNER_CHAT_ID = "7910616962"
VIP_CHANNEL_LINK = "https://t.me/+your_vip_invite_link"
BOT_USERNAME = "AIMoneyPulseBot"

AFFILIATE_LINKS = """
💎 *Start Earning With These AI Tools:*
- [Jasper AI — Write & Earn](https://www.jasper.ai)
- [Copy.ai — Automate Content](https://www.copy.ai)
- [Fiverr — Sell AI Services](https://www.fiverr.com)
- [GetResponse — Email Automation](https://www.getresponse.com)
"""

SUBSCRIBERS_FILE = "subscribers.json"
WEEKLY_TIPS_FILE = "weekly_tips.json"

def load_subscribers():
    if os.path.exists(SUBSCRIBERS_FILE):
        with open(SUBSCRIBERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_subscribers(subs):
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(subs, f)

def add_subscriber(chat_id, username="", preferences=None):
    subs = load_subscribers()
    subs[str(chat_id)] = {
        "username": username,
        "preferences": preferences or ["all"],
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "referrals": 0
    }
    save_subscribers(subs)

def load_weekly_tips():
    if os.path.exists(WEEKLY_TIPS_FILE):
        with open(WEEKLY_TIPS_FILE, "r") as f:
            return json.load(f)
    return []

def save_weekly_tips(tips):
    with open(WEEKLY_TIPS_FILE, "w") as f:
        json.dump(tips, f)

def ask_groq(prompt, system_prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.9,
        "max_tokens": 600
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"Groq error: {response.text}")
            return None
    except Exception as e:
        print(f"Groq exception: {e}")
        return None

def generate_daily_news():
    system = (
        "You are an expert in AI tools and online money-making opportunities. "
        "You deliver short, punchy, exciting daily updates about the hottest ways "
        "people are using AI to make money online RIGHT NOW. "
        "Use emojis generously. Format for Telegram using *bold* for key points. "
        "Keep it under 280 words. Always end with a powerful motivating call to action."
    )
    prompt = (
        "Give me today's AI money-making update. Include:\n"
        "1. 🔥 One hot AI tool or trend blowing up RIGHT NOW\n"
        "2. 💰 Realistic income people are making with it (be specific)\n"
        "3. 🚀 3 simple steps a beginner can take TODAY to start\n"
        "4. 🎯 One power tip most people miss\n"
        "End with an exciting motivating line."
    )
    return ask_groq(prompt, system)

def generate_quick_tip():
    system = (
        "You are an AI money-making expert. Give one short, powerful, actionable tip "
        "about making money with AI. Use emojis. Max 100 words. Format for Telegram."
    )
    prompt = "Give me one powerful AI money-making tip I can act on today."
    return ask_groq(prompt, system)

def generate_weekly_roundup(tips):
    system = (
        "You are an AI money-making expert creating a weekly roundup. "
        "Summarize the week's best AI money tips in an exciting, punchy format. "
        "Use emojis. Format for Telegram. Max 300 words."
    )
    tips_text = "\n".join(tips[-7:]) if tips else "AI automation, content creation, chatbot services"
    prompt = f"Create an exciting weekly roundup of these AI money-making tips:\n{tips_text}"
    return ask_groq(prompt, system)

def send_message(chat_id, text, parse_mode="Markdown", reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Send error: {e}")
        return False

def broadcast(text):
    subs = load_subscribers()
    success = 0
    for chat_id in subs:
        if send_message(chat_id, text):
            success += 1
        time.sleep(0.1)
    send_message(OWNER_CHAT_ID, text)
    print(f"✅ Broadcast sent to {success} subscribers")

def answer_callback(callback_query_id, text=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    requests.post(url, json={"callback_query_id": callback_query_id, "text": text}, timeout=10)

def handle_start(chat_id, username, args=""):
    add_subscriber(chat_id, username)
    if args:
        subs = load_subscribers()
        referrer = args.strip()
        if referrer in subs and referrer != str(chat_id):
            subs[referrer]["referrals"] = subs[referrer].get("referrals", 0) + 1
            save_subscribers(subs)
    welcome = (
        f"🤖 *Welcome to AI Money Pulse!*\n\n"
        f"You're now plugged into the #1 daily feed for AI money-making opportunities. 💰\n\n"
        f"*What you'll get:*\n"
        f"🔥 Daily AI money news every morning at 8AM\n"
        f"💡 Quick tips on demand\n"
        f"📊 Weekly roundups every Sunday\n"
        f"🔗 Curated tools to start earning\n\n"
        f"*Quick commands:*\n"
        f"/tip — Get an instant AI money tip\n"
        f"/news — Get today's update now\n"
        f"/vip — Unlock premium content\n"
        f"/refer — Get your referral link\n"
        f"/stats — See your referral stats\n\n"
        f"Let's get you making money with AI! 🚀"
    )
    keyboard = {
        "inline_keyboard": [
            [{"text": "💡 Get a Quick Tip", "callback_data": "quick_tip"}],
            [{"text": "💎 Go VIP", "callback_data": "vip"}, {"text": "🔗 Refer & Earn", "callback_data": "refer"}]
        ]
    }
    send_message(chat_id, welcome, reply_markup=keyboard)

def handle_tip(chat_id):
    send_message(chat_id, "⏳ Generating your AI money tip...")
    tip = generate_quick_tip()
    if tip:
        msg = f"💡 *AI Money Tip*\n\n{tip}\n\n{AFFILIATE_LINKS}"
        send_message(chat_id, msg)
    else:
        send_message(chat_id, "❌ Couldn't generate tip right now. Try again!")

def handle_news(chat_id):
    send_message(chat_id, "⏳ Fetching today's AI money news...")
    news = generate_daily_news()
    if news:
        msg = f"📰 *Today's AI Money Update*\n\n{news}\n\n{AFFILIATE_LINKS}"
        send_message(chat_id, msg)
    else:
        send_message(chat_id, "❌ Couldn't fetch news right now. Try again shortly!")

def handle_vip(chat_id):
    msg = (
        f"💎 *Go VIP — Unlock Premium AI Money Content*\n\n"
        f"*What VIP members get:*\n"
        f"🔐 Exclusive deep-dive strategies\n"
        f"📈 Advanced AI income blueprints\n"
        f"🤝 Private community access\n"
        f"⚡ Early access to new opportunities\n"
        f"📞 Monthly Q&A sessions\n\n"
        f"💰 *Only $10/month — less than a coffee per week!*\n\n"
        f"👇 Join the VIP channel now:"
    )
    keyboard = {
        "inline_keyboard": [
            [{"text": "💎 Join VIP Now", "url": VIP_CHANNEL_LINK}]
        ]
    }
    send_message(chat_id, msg, reply_markup=keyboard)

def handle_refer(chat_id):
    referral_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
    msg = (
        f"🔗 *Your Referral Link*\n\n"
        f"Share this link and grow your network:\n"
        f"`{referral_link}`\n\n"
        f"*How it works:*\n"
        f"👥 Every person who joins through your link is tracked\n"
        f"🏆 Top referrers get VIP access FREE\n"
        f"💰 Future referral rewards coming soon!\n\n"
        f"Share it everywhere — Whatsapp, Instagram, Facebook! 🚀"
    )
    send_message(chat_id, msg)

def handle_stats(chat_id):
    subs = load_subscribers()
    user = subs.get(str(chat_id), {})
    referrals = user.get("referrals", 0)
    total_subs = len(subs)
    msg = (
        f"📊 *Your Stats*\n\n"
        f"👥 Total subscribers: *{total_subs}*\n"
        f"🔗 Your referrals: *{referrals}*\n"
        f"📅 Joined: *{user.get('joined', 'N/A')}*\n\n"
        f"Keep sharing to climb the leaderboard! 🏆"
    )
    send_message(chat_id, msg)

def daily_news_job():
    print(f"⏰ [{datetime.now()}] Sending daily news...")
    news = generate_daily_news()
    if news:
        today = datetime.now().strftime("%A, %B %d")
        msg = (
            f"🌅 *Good Morning! AI Money Update — {today}*\n\n"
            f"{news}\n\n"
            f"{AFFILIATE_LINKS}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💎 Want deeper strategies? /vip\n"
            f"🔗 Share & earn rewards: /refer"
        )
        broadcast(msg)
        tips = load_weekly_tips()
        tips.append(news[:200])
        save_weekly_tips(tips)
    else:
        print("❌ Failed to generate daily news")

def weekly_roundup_job():
    print(f"⏰ [{datetime.now()}] Sending weekly roundup...")
    tips = load_weekly_tips()
    roundup = generate_weekly_roundup(tips)
    if roundup:
        msg = (
            f"📊 *Weekly AI Money Roundup*\n\n"
            f"{roundup}\n\n"
            f"{AFFILIATE_LINKS}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💎 Go deeper with VIP: /vip\n"
            f"🔗 Refer friends: /refer"
        )
        broadcast(msg)
        save_weekly_tips([])
    else:
        print("❌ Failed to generate weekly roundup")

def get_updates(offset=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"
    params = {"timeout": 30, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=35)
        if response.status_code == 200:
            return response.json().get("result", [])
    except Exception as e:
        print(f"Polling error: {e}")
    return []

def process_update(update):
    if "callback_query" in update:
        cb = update["callback_query"]
        chat_id = cb["message"]["chat"]["id"]
        data = cb.get("data", "")
        answer_callback(cb["id"])
        if data == "quick_tip":
            handle_tip(chat_id)
        elif data == "vip":
            handle_vip(chat_id)
        elif data == "refer":
            handle_refer(chat_id)
        return
    if "message" not in update:
        return
    msg = update["message"]
    chat_id = msg["chat"]["id"]
    username = msg["from"].get("username", msg["from"].get("first_name", "friend"))
    text = msg.get("text", "")
    if text.startswith("/start"):
        args = text[7:].strip() if len(text) > 7 else ""
        handle_start(chat_id, username, args)
    elif text == "/tip":
        handle_tip(chat_id)
    elif text == "/news":
        handle_news(chat_id)
    elif text == "/vip":
        handle_vip(chat_id)
    elif text == "/refer":
        handle_refer(chat_id)
    elif text == "/stats":
        handle_stats(chat_id)
    else:
        send_message(chat_id, (
            "👋 Use these commands:\n"
            "/tip — Quick AI money tip\n"
            "/news — Today's update\n"
            "/vip — Go premium\n"
            "/refer — Referral link\n"
            "/stats — Your stats"
        ))

def main():
    print("🤖 AI Money Pulse Bot STARTING...")
    add_subscriber(OWNER_CHAT_ID, "owner")
    schedule.every().day.at("08:00").do(daily_news_job)
    schedule.every().sunday.at("09:00").do(weekly_roundup_job)
    send_message(OWNER_CHAT_ID, (
        "✅ *AI Money Pulse Bot is LIVE!*\n\n"
        "Daily news sends at 8:00 AM\n"
        "Weekly roundup every Sunday at 9:00 AM\n\n"
        "Use /tip, /news, /vip, /refer, /stats"
    ))
    print("✅ Bot is live! Listening for messages...")
    offset = None
    while True:
        schedule.run_pending()
        updates = get_updates(offset)
        for update in updates:
            process_update(update)
            offset = update["update_id"] + 1
        time.sleep(1)

if __name__ == "__main__":
    main()

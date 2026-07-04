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
SERPAPI_KEY = "0cbea76edf51046d0e1136fb5f0e41af29137f1a3aaf4f7e94da4aab4c86cb43"
VIP_CHANNEL_LINK = "https://t.me/+your_vip_invite_link"
BOT_USERNAME = "AIWealthFeedBot"
CHANNEL_ID = OWNER_CHAT_ID

AFFILIATE_LINKS = """
🔗 *Top Rated AI Tools To Start Earning:*
- [Jasper AI — Write & Earn](https://www.jasper.ai)
- [Copy.ai — Automate Content](https://www.copy.ai)
- [Fiverr — Sell AI Services](https://www.fiverr.com)
- [GetResponse — Email Automation](https://www.getresponse.com)
- [Midjourney — AI Art Income](https://www.midjourney.com)
"""

SUBSCRIBERS_FILE = "subscribers.json"
WEEKLY_TIPS_FILE = "weekly_tips.json"
USED_TOOLS_FILE = "used_tools.json"
MILESTONES = [10, 50, 100, 500, 1000, 5000, 10000]

def load_json(filename, default):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return default

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

def load_subscribers(): return load_json(SUBSCRIBERS_FILE, {})
def save_subscribers(d): save_json(SUBSCRIBERS_FILE, d)
def load_weekly_tips(): return load_json(WEEKLY_TIPS_FILE, [])
def save_weekly_tips(d): save_json(WEEKLY_TIPS_FILE, d)
def load_used_tools(): return load_json(USED_TOOLS_FILE, [])
def save_used_tools(d): save_json(USED_TOOLS_FILE, d)

def add_subscriber(chat_id, username=""):
    subs = load_subscribers()
    is_new = str(chat_id) not in subs
    subs[str(chat_id)] = {
        "username": username,
        "joined": datetime.now().strftime("%Y-%m-%d"),
        "referrals": subs.get(str(chat_id), {}).get("referrals", 0)
    }
    save_subscribers(subs)
    if is_new:
        count = len(subs)
        if count in MILESTONES:
            send_message(OWNER_CHAT_ID,
                f"🎉 *Milestone Reached!*\n\nYou now have *{count} subscribers!* 🚀\nKeep growing!")

def search_latest_ai_tool():
    used = load_used_tools()
    url = "https://serpapi.com/search"
    params = {
        "q": "best highest rated AI tool to make money online 2026",
        "api_key": SERPAPI_KEY,
        "num": 10,
        "tbm": "nws"
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            results = response.json()
            snippets = []
            for r in results.get("news_results", [])[:5]:
                title = r.get("title", "")
                snippet = r.get("snippet", "")
                if title not in used:
                    snippets.append(f"{title}: {snippet}")
            if snippets:
                used.extend([r.get("title", "") for r in results.get("news_results", [])[:5]])
                save_used_tools(used[-50:])
                return "\n".join(snippets)
    except Exception as e:
        print(f"Search error: {e}")
    return None

def fetch_tool_image(tool_name):
    url = "https://serpapi.com/search"
    params = {
        "q": f"{tool_name} AI tool logo official",
        "api_key": SERPAPI_KEY,
        "tbm": "isch",
        "num": 3
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200:
            results = response.json()
            images = results.get("images_results", [])
            if images:
                return images[0].get("original", None)
    except Exception as e:
        print(f"Image search error: {e}")
    return None

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
        "max_tokens": 800
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Groq error: {e}")
    return None

def generate_daily_post(search_context=None):
    system = (
        "You are a top AI income expert delivering daily reports on the highest rated "
        "AI tools people use to make real money online. Be specific, exciting and practical. "
        "Format for Telegram using *bold* and emojis. Keep under 350 words."
    )
    context = f"Latest news context:\n{search_context}\n\n" if search_context else ""
    prompt = (
        f"{context}"
        "Write today's AI money-making tool report. Include:\n\n"
        "🏆 FEATURED TOOL:\n"
        "- Exact tool name\n"
        "- Star rating out of 5 (e.g. ⭐⭐⭐⭐⭐)\n"
        "- Difficulty level: 🟢 Beginner / 🟡 Intermediate / 🔴 Advanced\n"
        "- What it does\n"
        "- 💰 Realistic monthly earnings with proof\n\n"
        "📖 STEP BY STEP (how to make money with it):\n"
        "Step 1, Step 2, Step 3, Step 4\n\n"
        "🎯 PRO TIP: One insider tip most people miss\n\n"
        "⏰ LIMITED DEAL: Any current free trial or discount available\n\n"
        "🏅 HONORABLE MENTIONS: 3 other hot AI tools briefly (one line each with rating)\n\n"
        "End with a powerful motivating call to action."
    )
    return ask_groq(prompt, system)

def generate_quick_tip():
    system = (
        "You are an AI income expert. Pick one specific highest rated AI tool "
        "people are making money with RIGHT NOW. Be specific with name, earnings "
        "and exact steps. Use emojis. Max 200 words. Format for Telegram."
    )
    prompt = (
        "Name one specific highest rated AI tool people are earning with today. "
        "Include: tool name, star rating, difficulty level, how much beginners earn, "
        "and 3 exact steps to start making money with it today."
    )
    return ask_groq(prompt, system)

def generate_top5_tools():
    system = (
        "You are an AI income expert. List the top 5 highest rated AI tools "
        "people are using to make money this week. Be specific and practical. "
        "Format for Telegram with emojis."
    )
    prompt = (
        "List the top 5 highest rated AI money-making tools right now. "
        "For each include: name, star rating, difficulty level, earning potential, "
        "and one sentence on how to make money with it."
    )
    return ask_groq(prompt, system)

def generate_weekly_roundup():
    tips = load_weekly_tips()
    system = (
        "You are an AI income expert creating a weekly roundup. "
        "Summarize the week's best AI money tools in an exciting format. "
        "Use emojis. Format for Telegram. Max 350 words."
    )
    tips_text = "\n".join(tips[-7:]) if tips else "AI automation, content creation, chatbot services"
    prompt = (
        f"Create an exciting weekly roundup based on these tools covered this week:\n{tips_text}\n\n"
        "Include: top tool of the week, total earning potential, best tip of the week, "
        "and what to watch for next week."
    )
    return ask_groq(prompt, system)

def generate_success_story():
    system = "You are an AI income expert sharing inspiring success stories. Format for Telegram. Max 150 words."
    prompt = "Share a short realistic success story of someone making money with an AI tool. Include the tool, how they used it and how much they made."
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

def send_photo(chat_id, image_url, caption, parse_mode="Markdown"):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": chat_id,
        "photo": image_url,
        "caption": caption,
        "parse_mode": parse_mode
    }
    try:
        response = requests.post(url, json=payload, timeout=15)
        return response.status_code == 200
    except Exception as e:
        print(f"Photo error: {e}")
        return False

def send_poll(chat_id, question, options):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPoll"
    payload = {
        "chat_id": chat_id,
        "question": question,
        "options": json.dumps(options),
        "is_anonymous": False
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Poll error: {e}")
        return False

def broadcast(text, image_url=None):
    subs = load_subscribers()
    success = 0
    for chat_id in subs:
        if image_url:
            if send_photo(chat_id, image_url, text):
                success += 1
        else:
            if send_message(chat_id, text):
                success += 1
        time.sleep(0.1)
    if image_url:
        send_photo(OWNER_CHAT_ID, image_url, text)
    else:
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
        f"🤖 *Welcome to AI Wealth Feed!*\n\n"
        f"Your daily source for the *highest rated AI money-making tools* 💰\n\n"
        f"*What you get every day:*\n"
        f"🏆 Top rated AI tool of the day\n"
        f"📖 Step by step money-making instructions\n"
        f"🖼️ Tool image with every post\n"
        f"⏰ Latest deals and free trials\n"
        f"🏅 Honorable mentions\n"
        f"📊 Weekly roundups every Sunday\n\n"
        f"*Commands:*\n"
        f"/tip — Instant AI money tool\n"
        f"/news — Today's full report\n"
        f"/tools — Top 5 this week\n"
        f"/story — Success story\n"
        f"/vip — Go premium\n"
        f"/refer — Your referral link\n"
        f"/stats — Your stats\n\n"
        f"Let's get you making money with AI! 🚀"
    )
    keyboard = {
        "inline_keyboard": [
            [{"text": "🏆 Today's Top Tool", "callback_data": "news"}],
            [{"text": "💡 Quick Tip", "callback_data": "quick_tip"}, {"text": "📊 Top 5 Tools", "callback_data": "tools"}],
            [{"text": "💎 Go VIP", "callback_data": "vip"}, {"text": "🔗 Refer & Earn", "callback_data": "refer"}]
        ]
    }
    send_message(chat_id, welcome, reply_markup=keyboard)

def handle_tip(chat_id):
    send_message(chat_id, "⏳ Finding the highest rated AI money tool for you...")
    tip = generate_quick_tip()
    if tip:
        first_line = tip.split("\n")[0] if tip else ""
        image_url = fetch_tool_image(first_line[:30])
        if image_url:
            send_photo(chat_id, image_url, f"💡 *AI Money Tool*\n\n{tip}\n\n{AFFILIATE_LINKS}")
        else:
            send_message(chat_id, f"💡 *AI Money Tool*\n\n{tip}\n\n{AFFILIATE_LINKS}")
    else:
        send_message(chat_id, "❌ Couldn't generate tip right now. Try again!")

def handle_news(chat_id):
    send_message(chat_id, "⏳ Searching for today's highest rated AI money tool...")
    context = search_latest_ai_tool()
    news = generate_daily_post(context)
    if news:
        first_line = news.split("\n")[0] if news else ""
        image_url = fetch_tool_image(first_line[:30])
        if image_url:
            send_photo(chat_id, image_url, f"📰 *Today's AI Money Report*\n\n{news}\n\n{AFFILIATE_LINKS}")
        else:
            send_message(chat_id, f"📰 *Today's AI Money Report*\n\n{news}\n\n{AFFILIATE_LINKS}")
    else:
        send_message(chat_id, "❌ Couldn't fetch report right now. Try again shortly!")

def handle_tools(chat_id):
    send_message(chat_id, "⏳ Loading top 5 AI money tools this week...")
    tools = generate_top5_tools()
    if tools:
        send_message(chat_id, f"📊 *Top 5 AI Money Tools This Week*\n\n{tools}\n\n{AFFILIATE_LINKS}")
    else:
        send_message(chat_id, "❌ Couldn't load tools right now. Try again!")

def handle_story(chat_id):
    send_message(chat_id, "⏳ Loading a success story...")
    story = generate_success_story()
    if story:
        send_message(chat_id, f"🌟 *AI Income Success Story*\n\n{story}\n\n💎 You could be next! /vip")
    else:
        send_message(chat_id, "❌ Couldn't load story right now. Try again!")

def handle_vip(chat_id):
    msg = (
        f"💎 *Go VIP — Premium AI Money Intelligence*\n\n"
        f"*VIP members get:*\n"
        f"🔐 Exclusive deep-dive tool reviews\n"
        f"📈 Advanced income blueprints\n"
        f"⚡ Early access to new tools\n"
        f"🤝 Private community\n"
        f"📞 Monthly live Q&A\n"
        f"🎯 Done-for-you setup guides\n\n"
        f"💰 *Only $10/month*\n\n"
        f"👇 Join VIP now:"
    )
    keyboard = {"inline_keyboard": [[{"text": "💎 Join VIP Now", "url": VIP_CHANNEL_LINK}]]}
    send_message(chat_id, msg, reply_markup=keyboard)

def handle_refer(chat_id):
    referral_link = f"https://t.me/{BOT_USERNAME}?start={chat_id}"
    msg = (
        f"🔗 *Your Referral Link*\n\n"
        f"`{referral_link}`\n\n"
        f"*Rewards:*\n"
        f"👥 Every referral is tracked\n"
        f"🏆 Top referrers get FREE VIP\n"
        f"💰 Cash rewards coming soon!\n\n"
        f"Share on WhatsApp, Instagram, Facebook! 🚀"
    )
    send_message(chat_id, msg)

def handle_stats(chat_id):
    subs = load_subscribers()
    user = subs.get(str(chat_id), {})
    msg = (
        f"📊 *Your Stats*\n\n"
        f"👥 Total subscribers: *{len(subs)}*\n"
        f"🔗 Your referrals: *{user.get('referrals', 0)}*\n"
        f"📅 Joined: *{user.get('joined', 'N/A')}*\n\n"
        f"Keep sharing to climb the leaderboard! 🏆"
    )
    send_message(chat_id, msg)

def morning_post():
    print(f"⏰ [{datetime.now()}] Sending morning post...")
    context = search_latest_ai_tool()
    news = generate_daily_post(context)
    if news:
        today = datetime.now().strftime("%A, %B %d")
        first_line = news.split("\n")[0] if news else ""
        image_url = fetch_tool_image(first_line[:30])
        msg = (
            f"🌅 *Good Morning! AI Money Report — {today}*\n\n"
            f"{news}\n\n"
            f"{AFFILIATE_LINKS}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💎 Go deeper: /vip\n"
            f"🔗 Refer & earn: /refer"
        )
        broadcast(msg, image_url)
        tips = load_weekly_tips()
        tips.append(news[:200])
        save_weekly_tips(tips)

def evening_post():
    print(f"⏰ [{datetime.now()}] Sending evening post...")
    story = generate_success_story()
    tip = generate_quick_tip()
    if story and tip:
        msg = (
            f"🌆 *Evening AI Money Boost*\n\n"
            f"🌟 *Success Story:*\n{story}\n\n"
            f"💡 *Quick Tip:*\n{tip}\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💎 Go VIP for more: /vip"
        )
        broadcast(msg)

def weekly_poll():
    print(f"⏰ [{datetime.now()}] Sending weekly poll...")
    subs = load_subscribers()
    poll_options = [
        "🎨 AI Art & Design Tools",
        "✍️ AI Writing & Content",
        "🤖 AI Chatbot Services",
        "📈 AI Trading & Finance",
        "🎥 AI Video Creation"
    ]
    for chat_id in subs:
        send_poll(chat_id, "🗳️ Which AI money-making category should we feature next week?", poll_options)
    send_poll(OWNER_CHAT_ID, "🗳️ Which AI money-making category should we feature next week?", poll_options)

def weekly_roundup_job():
    print(f"⏰ [{datetime.now()}] Sending weekly roundup...")
    roundup = generate_weekly_roundup()
    if roundup:
        msg = (
            f"📊 *Weekly AI Money Roundup*\n\n"
            f"{roundup}\n\n"
            f"{AFFILIATE_LINKS}\n"
            f"━━━━━━━━━━━━━━━\n"
            f"💎 Go VIP: /vip | 🔗 Refer: /refer"
        )
        broadcast(msg)
        save_weekly_tips([])

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
        if data == "quick_tip": handle_tip(chat_id)
        elif data == "news": handle_news(chat_id)
        elif data == "tools": handle_tools(chat_id)
        elif data == "vip": handle_vip(chat_id)
        elif data == "refer": handle_refer(chat_id)
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
    elif text == "/tip": handle_tip(chat_id)
    elif text == "/news": handle_news(chat_id)
    elif text == "/tools": handle_tools(chat_id)
    elif text == "/story": handle_story(chat_id)
    elif text == "/vip": handle_vip(chat_id)
    elif text == "/refer": handle_refer(chat_id)
    elif text == "/stats": handle_stats(chat_id)
    else:
        send_message(chat_id, (
            "👋 *Commands:*\n"
            "/tip — Instant AI money tool\n"
            "/news — Today's full report\n"
            "/tools — Top 5 this week\n"
            "/story — Success story\n"
            "/vip — Go premium\n"
            "/refer — Referral link\n"
            "/stats — Your stats"
        ))

def main():
    print("🤖 AI Wealth Feed Bot STARTING...")
    add_subscriber(OWNER_CHAT_ID, "owner")
    schedule.every().day.at("08:00").do(morning_post)
    schedule.every().day.at("18:00").do(evening_post)
    schedule.every().sunday.at("09:00").do(weekly_roundup_job)
    schedule.every().friday.at("12:00").do(weekly_poll)
    send_message(OWNER_CHAT_ID, (
        "✅ *AI Wealth Feed Bot is LIVE!*\n\n"
        "📅 *Schedule:*\n"
        "🌅 Morning report: 8:00 AM daily\n"
        "🌆 Evening boost: 6:00 PM daily\n"
        "📊 Weekly roundup: Sunday 9:00 AM\n"
        "🗳️ Weekly poll: Friday 12:00 PM\n\n"
        "Commands: /tip /news /tools /story /vip /refer /stats"
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

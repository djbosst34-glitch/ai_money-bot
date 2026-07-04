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
        print(f"SerpAPI status: {response.status_code}")
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
        else:
            print(f"SerpAPI error: {response.text[:200]}")
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
        print(f"Groq status: {response.status_code}")
        print(f"Groq response: {response.text[:200]}")
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"Groq error: {response.text}")
            return None
    except Exception as e:
        print(f"Groq exception: {e}")
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

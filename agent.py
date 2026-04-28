# ================================
# 🚀 IMPORTS
# ================================
import requests
import smtplib
import json
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# ================================
# 🔑 API KEYS (replace later!)
# ================================
WEATHER_API_KEY = "8c566a50deee2104b3188209a773d570"
GOOGLE_API_KEY = "AIzaSyDRUkbtWDmpMrHVveHs0E7siunKzoDmeEI"


# ================================
# 🧠 MEMORY (STATE STORAGE)
# ================================
def load_state():
    """Load previous state from file"""
    if not os.path.exists("state.json"):
        return {}

    with open("state.json", "r") as f:
        return json.load(f)


def save_state(state):
    """Save current state to file"""
    with open("state.json", "w") as f:
        json.dump(state, f)


# ================================
# 📧 EMAIL NOTIFICATION
# ================================
def send_email(message):
    sender_email = "pranjal.sh7@gmail.com"
    app_password = "zidg pvef jhqd zxfr"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🏍️ Ride Decision"
    msg["From"] = sender_email
    msg["To"] = sender_email

    html_part = MIMEText(message, "html")
    msg.attach(html_part)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.send_message(msg)


# ================================
# 📱 PUSH + TELEGRAM
# ================================
def send_push(message):
    requests.post("https://api.pushover.net/1/messages.json", data={
        "token": "YOUR_PUSHOVER_APP_TOKEN",
        "user": "YOUR_PUSHOVER_USER_KEY",
        "message": message
    })


def send_telegram(message):
    token = "YOUR_TELEGRAM_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message})


# ================================
# 🌦 WEATHER + TRAFFIC
# ================================
def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/forecast?q=Seattle&units=imperial&appid={WEATHER_API_KEY}"
    return requests.get(url).json()


def get_commute_time():
    origin = "19728 11th Dr SE, Bothell, WA"
    destination = "1100 Olive Way, Seattle"

    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={origin}&destinations={destination}&departure_time=now&key={GOOGLE_API_KEY}"

    data = requests.get(url).json()

    try:
        return data["rows"][0]["elements"][0]["duration_in_traffic"]["text"]
    except:
        return "Unknown"


# ================================
# 🧠 DATA PROCESSING
# ================================
def get_commute_weather(data):
    """Split forecast into morning & evening windows"""
    morning, evening = [], []

    for entry in data["list"]:
        hour = int(entry["dt_txt"].split(" ")[1].split(":")[0])

        if 8 <= hour <= 10:
            morning.append(entry)
        if 15 <= hour <= 17:
            evening.append(entry)

    return morning, evening


def analyze_block(entries):
    """Extract key metrics"""
    if not entries:
        return None

    temps = [x["main"]["feels_like"] for x in entries]
    wind = [x["wind"]["speed"] for x in entries]
    pop = [x["pop"] for x in entries]

    return {
        "temp": sum(temps) / len(temps),
        "wind": max(wind),
        "pop": max(pop)
    }


# ================================
# 🏍 DECISION ENGINE
# ================================
def decide(block):
    if not block:
        return "Unknown"

    if block["pop"] > 0.3:
        return "❌ Rain"
    if block["temp"] < 45:
        return "❌ Cold"
    if block["wind"] > 20:
        return "❌ Windy"

    return "✅ Ride"


def build_summary(morning_decision, evening_decision):
    if "✅" in morning_decision and "✅" in evening_decision:
        return "👉 Ride both ways"
    elif "✅" in morning_decision:
        return "👉 Ride in morning, skip evening"
    elif "✅" in evening_decision:
        return "👉 Skip morning, ride in evening"
    else:
        return "👉 Better take the car today"


# ================================
# 🎨 UI HELPERS
# ================================
def colorize(text):
    if "✅" in text:
        return f'<span style="color:green;"><b>{text}</b></span>'
    elif "❌" in text:
        return f'<span style="color:red;"><b>{text}</b></span>'
    else:
        return f'<span style="color:orange;"><b>{text}</b></span>'


# ================================
# 📊 TREND ANALYZER
# ================================
def detect_trend(previous, current):
    trends = []

    if not previous:
        return trends

    # traffic trend
    try:
        prev_time = int(previous.get("commute_time", "0").split()[0])
        curr_time = int(current.get("commute_time", "0").split()[0])

        if curr_time > prev_time + 10:
            trends.append("🚨 Traffic getting worse")
        elif curr_time < prev_time - 10:
            trends.append("👍 Traffic improving")
    except:
        pass

    # summary change
    if previous.get("summary") != current.get("summary"):
        trends.append("🔄 Ride conditions changed")

    return trends


# ================================
# 🧾 MESSAGE BUILDER
# ================================

def build_messages(summary, morning, evening, commute_time):
    now = datetime.now().strftime("%A %I:%M %p")

    # 🗺️ Map data
    origin = "19728 11th Dr SE, Bothell, WA"
    destination = "1100 Olive Way, Seattle"

    maps_url = f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}&travelmode=driving"

    map_image_url = f"https://maps.googleapis.com/maps/api/staticmap?size=600x300&markers=color:green|{origin}&markers=color:red|{destination}&path=color:0x0000ff|{origin}|{destination}&key={GOOGLE_API_KEY}"

    # 📱 Short message
    short_msg = f"""{summary}

Morning: {morning}
Evening: {evening}

🚗 {commute_time}"""

    # 📧 HTML message (FIXED INDENT)
    html_msg = f"""
<html>
<body style="font-family:Arial; background:#f4f6f8; padding:20px;">
<div style="background:white; padding:20px; border-radius:10px; max-width:500px; margin:auto;">

<h2>🏍️ Ride Decision</h2>

<p><b>{summary}</b></p>
<p>🕒 {now}</p>

<table style="width:100%;">
<tr><td>Morning</td><td align="right">{colorize(morning)}</td></tr>
<tr><td>Evening</td><td align="right">{colorize(evening)}</td></tr>
</table>

<p>🚗 Commute Time: {commute_time}</p>

<hr>

<h3>🗺️ Route</h3>

<a href="{maps_url}">
    <img src="{map_image_url}" style="width:100%; border-radius:8px;">
</a>

<p>
<a href="{maps_url}">👉 Open in Google Maps</a>
</p>

</div>
</body>
</html>
"""

    return html_msg, short_msg


# ================================
# 📡 NOTIFICATIONS
# ================================
def notify_all(email_msg, short_msg, summary, trends, current_state):
    send_email(email_msg)

    if trends:
        send_push(f"📊 Trend Alert\n\n{short_msg}")
        send_telegram(f"📊 Trend Alert\n\n{short_msg}")
    elif "❌" in summary:
        send_push(short_msg)
        send_telegram(short_msg)

    save_state(current_state)


# ================================
# 🧠 ORCHESTRATOR (MAIN FLOW)
# ================================
def orchestrate():
    weather = get_weather()
    traffic = get_commute_time()

    if "list" not in weather:
        print("Weather API failed")
        return

    previous = load_state()

    morning_data, evening_data = get_commute_weather(weather)
    morning = analyze_block(morning_data)
    evening = analyze_block(evening_data)

    morning_decision = decide(morning)
    evening_decision = decide(evening)

    summary = build_summary(morning_decision, evening_decision)

    email_msg, short_msg = build_messages(
        summary,
        morning_decision,
        evening_decision,
        traffic
    )

    current_state = {
        "summary": summary,
        "commute_time": traffic
    }

    trends = detect_trend(previous, current_state)

    notify_all(email_msg, short_msg, summary, trends, current_state)


# ================================
# 🚀 RUN
# ================================
orchestrate()
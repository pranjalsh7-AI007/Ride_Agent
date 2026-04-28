# 🏍️ Motorcycle Ride Decision Agent

A smart, automated system that analyzes weather and traffic conditions to help decide whether to ride a motorcycle to work.

---

## 🚀 Features

- 🌦 **Weather Analysis**
  - Uses OpenWeather API
  - Evaluates rain probability, temperature, and wind

- 🚗 **Traffic Monitoring**
  - Uses Google Maps API
  - Calculates real-time commute time

- 🧠 **Smart Decision Logic**
  - Morning vs Evening commute decisions
  - Trend detection (improving or worsening conditions)

- 📊 **Trend Awareness**
  - Detects changes from previous runs
  - Alerts only when conditions change or worsen

- 📧 **Email Dashboard**
  - Styled HTML email with:
    - Ride recommendations
    - Commute time
    - Clean UI

- 📱 **Push Notifications (Optional)**
  - Pushover integration
  - Telegram bot support

- ☁️ **Cloud Automation**
  - Runs daily via GitHub Actions
  - No local machine required

---

## 🧠 How It Works

```text
Collect Data → Process → Decide → Detect Trends → Notify → Save State

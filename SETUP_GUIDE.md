# 🔗 TaskMate AI — WhatsApp Integration Setup Guide

> Complete step-by-step guide to connect TaskMate AI to WhatsApp using Twilio.

---

## 📋 Prerequisites

| Requirement | Link |
|---|---|
| Python 3.10+ | [python.org](https://www.python.org/downloads/) |
| Twilio Account (free trial) | [twilio.com/try-twilio](https://www.twilio.com/try-twilio) |
| OpenAI API Key | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| ngrok (free) | [ngrok.com/download](https://ngrok.com/download) |
| OpenWeatherMap Key *(optional)* | [openweathermap.org/api](https://openweathermap.org/api) |

---

## ⚡ Quick Setup (5 Minutes)

### 1️⃣ Install Dependencies

```bash
cd c:\Users\Administrator\Desktop\HACK
pip install -r requirements.txt
```

### 2️⃣ Get Your API Keys

#### Twilio (WhatsApp Gateway)
1. Sign up at [twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Verify your email and phone number
3. From the **Twilio Console Dashboard** ([console.twilio.com](https://console.twilio.com)):
   - Copy your **Account SID** (starts with `AC...`)
   - Copy your **Auth Token** (click "Show" to reveal it)

#### OpenAI (AI Brain)
1. Sign up at [platform.openai.com](https://platform.openai.com)
2. Go to **API Keys** → **Create new secret key**
3. Copy the key (starts with `sk-...`)

#### OpenWeatherMap *(Optional — for weather feature)*
1. Sign up at [openweathermap.org](https://openweathermap.org)
2. Go to **API Keys** tab → Copy your key

### 3️⃣ Configure Environment

```bash
copy .env.example .env
```

Open `.env` in your editor and fill in:

```env
# ─── REQUIRED ──────────────────────────────
OPENAI_API_KEY=sk-paste-your-openai-key-here
TWILIO_ACCOUNT_SID=ACpaste-your-sid-here
TWILIO_AUTH_TOKEN=paste-your-auth-token-here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# ─── OPTIONAL ──────────────────────────────
OPENWEATHER_API_KEY=paste-your-weather-key-here
```

### 4️⃣ Activate WhatsApp Sandbox

1. Go to **Twilio Console** → **Messaging** → **Try it out** → **Send a WhatsApp message**
   - Direct link: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. You'll see a sandbox number and a join code like:
   ```
   Send "join <code-word>" to +1 415 523 8886
   ```
3. **On your phone**: Open WhatsApp → Send that exact message to the number
4. You'll receive: *"You're connected to the sandbox!"*

### 5️⃣ Start the Server

```bash
python app.py
```

You should see:
```
============================================================
  🤖 TaskMate AI - WhatsApp Productivity Agent
  ✅ All configuration validated successfully!
  📡 Server running at http://0.0.0.0:8000
  📊 Dashboard at http://0.0.0.0:8000/
============================================================
```

### 6️⃣ Expose with ngrok

Open a **new terminal** (keep the server running):

```bash
ngrok http 8000
```

ngrok will display:
```
Forwarding  https://abc123.ngrok-free.app → http://localhost:8000
```

📌 **Copy the `https://...ngrok-free.app` URL** — you'll need it next.

### 7️⃣ Set Twilio Webhook

1. Go to **Twilio Console** → **Messaging** → **Settings** → **WhatsApp Sandbox Settings**
   - Direct link: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
2. In **"WHEN A MESSAGE COMES IN"**:
   ```
   https://YOUR-NGROK-URL/webhook
   ```
   *(Example: `https://abc123.ngrok-free.app/webhook`)*
3. Method: **POST**
4. Click **Save**

### 8️⃣ Test It! 🎉

Send messages from your WhatsApp to the Twilio sandbox number:

| Send This | Expected Response |
|---|---|
| `Hi` | 👋 Greeting + intro |
| `Remind me to call mom at 5pm` | ⏰ Reminder confirmation |
| `Add task: Buy groceries` | ✅ Task created |
| `Show my tasks` | 📋 Task list |
| `Done with groceries` | 🎉 Task completed |
| `Summarize: [paste long text]` | 📝 Concise summary |
| `Weather in Mumbai` | 🌤️ Real-time weather |
| `help` | 🤖 Full feature list |

---

## 🖥️ Dashboard

Open `http://localhost:8000` in your browser to:
- 💬 View chat logs in real-time
- ⏰ Monitor reminders
- 📋 Track tasks
- ⚡ See agent activity
- 🧪 Test with the built-in Chat Simulator

---

## ✅ Integration Checklist

```
[ ] Python dependencies installed (pip install -r requirements.txt)
[ ] .env file created with API keys
[ ] Twilio WhatsApp Sandbox activated
[ ] WhatsApp sandbox joined from your phone
[ ] Server running (python app.py)
[ ] ngrok running (ngrok http 8000)
[ ] Twilio webhook URL set to https://YOUR-NGROK-URL/webhook
[ ] Test message sent from WhatsApp
[ ] Dashboard verified at http://localhost:8000
```

---

## 🔧 Troubleshooting

| Issue | Fix |
|---|---|
| Server won't start | Check `.env` file exists and has valid keys |
| WhatsApp not responding | Verify ngrok URL in Twilio webhook settings |
| "AI service error" | Check your `OPENAI_API_KEY` is valid and has credits |
| Weather not working | Add `OPENWEATHER_API_KEY` to `.env` |
| ngrok URL changed | Update Twilio webhook (ngrok URL changes on restart unless paid) |
| "Not connected to sandbox" | Re-send the `join` message from WhatsApp |

---

## 🚀 For Demo Day

1. Start server: `python app.py`
2. Start ngrok: `ngrok http 8000`
3. Update Twilio webhook with new ngrok URL
4. Open dashboard: `http://localhost:8000`
5. Demo from WhatsApp + show dashboard simultaneously

> **Pro Tip**: Use ngrok's paid plan ($8/mo) to get a **fixed URL** that never changes — eliminates step 3!

---

## 📌 API Endpoints Reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Dashboard UI |
| `/health` | GET | Health check |
| `/webhook` | POST | Twilio WhatsApp webhook |
| `/api/simulate` | POST | Chat simulator (no Twilio needed) |
| `/api/stats` | GET | Dashboard statistics |
| `/api/conversations` | GET | Chat logs |
| `/api/reminders` | GET | All reminders |
| `/api/tasks` | GET | All tasks |
| `/api/logs` | GET | Agent activity logs |

---

<p align="center">
  <strong>TaskMate AI</strong> — Your Productivity, One Message Away 🚀
</p>

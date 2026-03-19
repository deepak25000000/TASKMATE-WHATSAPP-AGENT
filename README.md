# 🤖 TaskMate AI — WhatsApp Productivity Agent

> **Airia AI Agent Challenge · Airia Everywhere Track**
> An intelligent WhatsApp-based AI assistant that manages daily productivity tasks through natural language conversations.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green?logo=fastapi)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT-blueviolet?logo=openai)
![Twilio](https://img.shields.io/badge/Twilio-WhatsApp-red?logo=twilio)

---

## 📌 Problem

Users constantly switch between multiple apps — calendars, notes, reminders, search tools — leading to inefficiency, distraction, and lost productivity. There's no unified conversational interface that handles all daily productivity needs.

## ✅ Solution

**TaskMate AI** is a WhatsApp-based AI agent that:
- 🗣️ Understands natural language inputs
- ⏰ Sets reminders and manages tasks
- 📝 Summarizes long text and notes
- 🌤️ Fetches real-time weather
- 🧠 Maintains conversational memory across sessions
- 🤖 Makes autonomous decisions with multi-step reasoning

---

## 🏗️ System Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────────────────┐
│   WhatsApp   │────▶│  Twilio API  │────▶│   FastAPI Backend (app.py)│
│   (User)     │◀────│  (Gateway)   │◀────│                           │
└──────────────┘     └──────────────┘     │  ┌────────────────────┐  │
                                          │  │  Intent Detection   │  │
                                          │  │  (agent/intent.py)  │  │
                                          │  └─────────┬──────────┘  │
                                          │            ▼             │
                                          │  ┌────────────────────┐  │
                                          │  │  Action Router      │  │
                                          │  │  (agent/actions.py) │  │
                                          │  └─────────┬──────────┘  │
                                          │            ▼             │
                                          │  ┌────────────────────┐  │
                                          │  │  Memory System      │  │
                                          │  │  (agent/memory.py)  │  │
                                          │  └────────────────────┘  │
                                          │                          │
                                          │  ┌─────────┐ ┌────────┐ │
                                          │  │ OpenAI  │ │Weather │ │
                                          │  │ Service │ │Service │ │
                                          │  └─────────┘ └────────┘ │
                                          │                          │
                                          │  ┌────────────────────┐  │
                                          │  │  SQLite Database    │  │
                                          │  │  (database/db.py)   │  │
                                          │  └────────────────────┘  │
                                          └──────────────────────────┘
```

---

## ⚙️ Features

| Feature | Description |
|---------|-------------|
| 🗣️ **Natural Language Processing** | Understands conversational inputs via GPT + regex |
| 🎯 **Intent Detection** | Classifies reminders, tasks, weather, summarization, etc. |
| ⏰ **Smart Reminders** | "Remind me to call mom at 5pm" → stored & confirmed |
| 📋 **Task Management** | Create, list, complete tasks with priority levels |
| 📝 **Text Summarization** | Condense long notes into key points |
| 🌤️ **Weather API** | Real-time weather from OpenWeatherMap |
| 🧠 **Conversation Memory** | Tracks last 10 messages per user for context |
| 💡 **Smart Suggestions** | Proactive follow-up recommendations |
| 📊 **Web Dashboard** | Real-time monitoring with glassmorphism UI |
| 🧪 **Chat Simulator** | Test the agent without Twilio setup |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
cd HACK
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

Required keys:
- `OPENAI_API_KEY` — Get from [OpenAI Platform](https://platform.openai.com)
- `TWILIO_ACCOUNT_SID` + `TWILIO_AUTH_TOKEN` — From [Twilio Console](https://console.twilio.com)
- `OPENWEATHER_API_KEY` — From [OpenWeatherMap](https://openweathermap.org/api)

### 3. Run the Server

```bash
python app.py
```

The server starts at **http://localhost:8000**

### 4. Open Dashboard

Navigate to `http://localhost:8000` to access the dashboard with the built-in chat simulator.

### 5. Connect Twilio WhatsApp (Optional)

1. Set up [Twilio WhatsApp Sandbox](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Set your webhook URL: `https://your-domain.com/webhook` (POST)
3. Use [ngrok](https://ngrok.com) for local development: `ngrok http 8000`

---

## 📁 Project Structure

```
/HACK
├── app.py                    # FastAPI server + webhook + API
├── config.py                 # Environment configuration
├── requirements.txt          # Python dependencies
├── .env.example              # Environment template
├── README.md                 # Documentation
│
├── agent/                    # AI Agent Logic
│   ├── intent.py             # Intent detection (regex + GPT)
│   ├── actions.py            # Action router + handlers
│   └── memory.py             # Conversation memory system
│
├── services/                 # External Service Integrations
│   ├── openai_service.py     # OpenAI GPT wrapper
│   ├── whatsapp_service.py   # Twilio WhatsApp service
│   └── weather_service.py    # OpenWeatherMap integration
│
├── database/                 # Data Layer
│   └── db.py                 # SQLite database + CRUD
│
├── dashboard/                # Web Dashboard
│   ├── index.html            # Dashboard UI
│   ├── style.css             # Premium dark theme CSS
│   └── app.js                # Client-side logic
│
└── utils/                    # Utilities
    └── helpers.py            # Helper functions
```

---

## 🧠 Agent Workflow

```
User Message → Twilio Webhook → Intent Detection → Action Routing → Response
                                      │                    │
                                      ▼                    ▼
                                 GPT Fallback         Execute Handler
                                (low confidence)    (reminder/task/weather...)
                                      │                    │
                                      ▼                    ▼
                                Memory Update ◀───── Generate Response
                                      │
                                      ▼
                              Send via WhatsApp/TwiML
```

---

## 💬 Example Interactions

| Message | Intent | Response |
|---------|--------|----------|
| "Remind me to call mom at 5pm" | `reminder` | ⏰ Reminder Set! Call mom at 5:00 PM |
| "Add task: Buy groceries" | `task_create` | ✅ Task Created! Buy groceries [Medium] |
| "Show my tasks" | `task_list` | 📋 Your Tasks (3 pending)... |
| "Done with groceries" | `task_complete` | 🎉 Task Completed! ~~Buy groceries~~ |
| "Weather in Tokyo" | `weather` | ☀️ Weather in Tokyo: 22°C, Clear |
| "Summarize: [long text]" | `summarize` | 📋 Summary: Key points... |
| "Hi" | `greeting` | 👋 Good morning! I'm TaskMate AI... |
| "help" | `help` | 🤖 Here's what I can do... |

---

## 🧪 Testing

### Chat Simulator (No Twilio Required)
Open `http://localhost:8000` and use the built-in chat simulator.

### API Testing
```bash
# Health check
curl http://localhost:8000/health

# Simulate a message
curl -X POST http://localhost:8000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"phone": "whatsapp:+1234567890", "message": "Remind me to study at 6pm"}'

# Get stats
curl http://localhost:8000/api/stats
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python, FastAPI |
| AI Engine | OpenAI GPT-3.5/4 |
| Messaging | Twilio WhatsApp API |
| Database | SQLite |
| Weather | OpenWeatherMap API |
| Dashboard | HTML, CSS (Glassmorphism), JavaScript |

---

## 👥 Target Users

- 🎓 **Students** — Managing assignments and schedules
- 💼 **Professionals** — Managing meetings and tasks
- 🧑‍💻 **Freelancers** — Handling daily workflows
- 🌐 **Anyone** — Seeking a simple productivity tool via WhatsApp

---

## 📜 License

Built for the **Airia AI Agent Challenge — Airia Everywhere Track**.

---

<p align="center">
  <strong>TaskMate AI</strong> — Your Productivity, One Message Away 🚀
</p>

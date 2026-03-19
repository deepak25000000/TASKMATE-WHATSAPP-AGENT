# 🛠️ TaskMate AI — WhatsApp Webhook Fix Guide

> Your agent is running but WhatsApp replies with the default Twilio message instead.
> This guide fixes that in **2 minutes**.

---

## ❌ The Problem

When you send a message on WhatsApp, you get:
```
"You said: [your message]. Configure your WhatsApp Sandbox's Inbound URL to change this message."
```

**Why?** Twilio doesn't know where to forward your messages. You need to tell Twilio:
*"Send all incoming WhatsApp messages to MY server."*

---

## ✅ The Fix (Step by Step)

### Step 1: Confirm Your Server is Running

Your server should already be running. Verify by opening this in your browser:
```
http://localhost:8000/health
```

You should see: `{"status": "healthy", "service": "TaskMate AI"}`

If NOT running, start it:
```bash
cd c:\Users\Administrator\Desktop\HACK
python app.py
```

---

### Step 2: Confirm ngrok is Running

ngrok creates a public URL for your local server. Open this in your browser:
```
http://localhost:4040
```

You'll see your **public ngrok URL** displayed, something like:
```
https://2692-106-193-207-77.ngrok-free.app
```

📌 **Copy this URL** — you need it in Step 3.

If ngrok is NOT running, start it in a **new terminal**:
```bash
ngrok http 8000
```

---

### Step 3: Set Webhook URL in Twilio ⭐ (THIS IS THE FIX)

This is the step that fixes everything:

1. **Open your browser** and go to:
   ```
   https://console.twilio.com
   ```

2. **Log in** with your Twilio email and password.

3. **Navigate to Sandbox Settings** — after logging in, go to:
   ```
   https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
   ```

   **OR** navigate manually:
   - Left sidebar → **Messaging**
   - Click → **Settings**
   - Click → **WhatsApp Sandbox Settings**

4. **Find the field** labeled:
   ```
   WHEN A MESSAGE COMES IN
   ```

5. **Paste your webhook URL** in that field:
   ```
   https://YOUR-NGROK-URL/webhook
   ```

   For example, if your ngrok URL is `https://2692-106-193-207-77.ngrok-free.app`, paste:
   ```
   https://2692-106-193-207-77.ngrok-free.app/webhook
   ```

   ⚠️ **IMPORTANT**: Don't forget `/webhook` at the end!

6. **Set the method** to: **POST**

7. **Click the SAVE button** at the bottom of the page.

---

### Step 4: Test on WhatsApp 🎉

Open WhatsApp on your phone. In the chat with the Twilio number (+14155238886), send:

```
Hi
```

**Expected result**: Instead of the default Twilio message, you should now see:

```
👋 Good afternoon! I'm TaskMate AI, your productivity assistant.
How can I help you today? Type help to see what I can do! 🚀
```

---

### Step 5: Try More Commands

Now try these messages one by one:

```
Remind me to submit assignment at 5pm
```

```
Add task: Complete project report
```

```
Show my tasks
```

```
help
```

```
Weather in Delhi
```

Each message will be processed by your AI agent and you'll get a smart reply! ✅

---

## 📊 Watch It Live

Open `http://localhost:8000` in your browser while you chat on WhatsApp.
You'll see every message, reminder, task, and agent action appear in real-time on the dashboard!

---

## 🔄 If ngrok URL Changes

ngrok gives a new URL every time you restart it. If that happens:
1. Check your new URL at `http://localhost:4040`
2. Go back to Twilio Sandbox Settings
3. Update the webhook URL with the new ngrok URL + `/webhook`
4. Save

---

## 🔍 Troubleshooting

| Problem | Solution |
|---|---|
| Still getting default Twilio message | Double-check the webhook URL ends with `/webhook` and method is POST |
| "502 Bad Gateway" in ngrok | Your Python server crashed — restart it with `python app.py` |
| ngrok shows "no tunnels" | Restart ngrok: `ngrok http 8000` |
| WhatsApp says "not connected to sandbox" | Re-send the join code (e.g., `join fifth-square`) |
| Agent replies with error | Check your `.env` has valid `OPENAI_API_KEY` |

---

## ✅ Summary Checklist

```
[ ] Server running (python app.py) → check http://localhost:8000/health
[ ] ngrok running (ngrok http 8000) → check http://localhost:4040
[ ] Twilio webhook set to: https://YOUR-NGROK-URL/webhook (POST)
[ ] Sandbox joined (sent "join fifth-square" on WhatsApp)
[ ] Test message sent → Agent replies ✅
```

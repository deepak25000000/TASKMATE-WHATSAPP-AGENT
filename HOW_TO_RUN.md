# 🔄 How to Run TaskMate AI (Daily Workflow)

> ⚠️ **IMPORTANT**: Because you are using the *free* version of ngrok, **your ngrok URL changes every single time you restart ngrok**. 
> 
> This means **every time you sit down to work/test**, you MUST update Twilio with the new URL, or WhatsApp will not connect to your server.

Here is the exact step-by-step process you must follow every time you start up the project.

---

## 🏃‍♂️ Step 1: Start Your Background Services

Open **two separate terminals** inside your project folder (`c:\Users\Administrator\Desktop\HACK`).

**Terminal 1 (The Server):**
```bash
python app.py
```
*(Leave this running. It processes the AI logic और dashboard).*

**Terminal 2 (ngrok):**
```bash
ngrok http 8000
```
*(Leave this running. It connects your local server to the internet).*

---

## 🔗 Step 2: Get Your New ngrok URL

Every time you run the command in Terminal 2, ngrok generates a random new URL. 

To easily copy it:
1. Open your browser and go to: **[http://localhost:4040](http://localhost:4040)**
2. Look at the top left for the URL (e.g., `https://1a2b-3c4d...ngrok-free.app`)
3. **Copy that `https://...` URL.**

---

## ⚙️ Step 3: Tell Twilio the New URL

Now you must tell Twilio where to forward WhatsApp messages:

1. Open your browser and go to: **[Twilio Sandbox Settings](https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox)**
2. In the field labeled **"WHEN A MESSAGE COMES IN"**, paste your new URL and add `/webhook` to the end.
   - ✅ **CORRECT**: `https://1a2b-3c4d.ngrok-free.app/webhook`
   - ❌ **WRONG**: `https://1a2b-3c4d.ngrok-free.app` *(missing /webhook)*
3. Make sure the dropdown next to it says **POST**.
4. Click the blue **Save** button at the bottom.

---

## 📱 Step 4: Re-Join the Sandbox (If Needed)

The Twilio Sandbox connection expires every 72 hours. 

1. Open WhatsApp on your phone.
2. Check your Twilio Sandbox Settings page for your join code (e.g., `join sugar-fly`).
3. Send that join code to the Twilio number (`+14155238886`).
4. You should get a reply saying *"You are connected!"*

---

## 🎉 Step 5: Start Chatting!

You are now fully connected. Send a message to your agent on WhatsApp:
```
Hi
```
```
Remind me to review my hackathon project at 8pm
```

Your agent will reply instantly!

---

### 💡 Pro Hack: How to stop the URL from changing

If you don't want to do Step 2 and Step 3 every time, you have two options:
1. **Never close ngrok**: If you just leave your computer running and never close that terminal, the URL stays active.
2. **Upgrade ngrok**: The $8/month ngrok plan gives you a permanent, fixed URL that never changes!

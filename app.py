"""
TaskMate AI - Main Application
FastAPI server with Twilio webhook, dashboard API, and static file serving.
"""

import sys
import os
import uvicorn
from datetime import datetime
from contextlib import asynccontextmanager

from typing import Optional
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from config import Config
from database.db import Database
from agent.memory import ConversationMemory
from agent.intent import detect_intent
from agent.actions import ActionRouter
from services.openai_service import AIService
from services.whatsapp_service import WhatsAppService
from services.weather_service import WeatherService


# ─── Application Lifespan ────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup, cleanup on shutdown."""
    # Startup
    print("\n" + "=" * 60)
    print("  🤖 TaskMate AI - WhatsApp Productivity Agent")
    print("  " + "=" * 56)

    # Validate configuration
    warnings = Config.validate()
    if warnings:
        for w in warnings:
            print(f"  {w}")
    else:
        print("  ✅ All configuration validated successfully!")

    # Initialize services
    app.state.db = Database(Config.DATABASE_PATH)
    app.state.memory = ConversationMemory(app.state.db, Config.MAX_MEMORY_MESSAGES)
    app.state.ai_service = AIService()
    app.state.weather_service = WeatherService()
    app.state.whatsapp_service = WhatsAppService()

    app.state.action_router = ActionRouter(
        db=app.state.db,
        memory=app.state.memory,
        openai_service=app.state.ai_service,
        weather_service=app.state.weather_service
    )

    print(f"\n  📡 Server running at http://{Config.HOST}:{Config.PORT}")
    print(f"  📊 Dashboard at http://{Config.HOST}:{Config.PORT}/")
    print(f"  🔗 Webhook URL: http://YOUR_DOMAIN:{Config.PORT}/webhook")
    print("=" * 60 + "\n")

    yield

    # Shutdown
    print("\n👋 TaskMate AI shutting down...")


# ─── FastAPI App ──────────────────────────────────────────────────

app = FastAPI(
    title="TaskMate AI",
    description="WhatsApp Productivity Agent powered by AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount dashboard static files
dashboard_dir = os.path.join(os.path.dirname(__file__), "dashboard")
if os.path.exists(dashboard_dir):
    app.mount("/static", StaticFiles(directory=dashboard_dir), name="static")


# ─── Dashboard Route ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the dashboard HTML."""
    index_path = os.path.join(dashboard_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>TaskMate AI - Dashboard not found</h1>", status_code=404)


# ─── Health Check ─────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "TaskMate AI",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


# ─── Twilio WhatsApp Webhook ─────────────────────────────────────

@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Handle incoming WhatsApp messages from Twilio."""
    try:
        form_data = await request.form()
        form_dict = dict(form_data)

        # Parse incoming message
        incoming = WhatsAppService.parse_incoming_message(form_dict)
        user_phone = incoming["from"]
        message_body = incoming["body"]
        profile_name = incoming["profile_name"]

        if not message_body:
            twiml = WhatsAppService.create_twiml_response(
                "👋 Hi! I'm TaskMate AI. Send me a text message to get started!"
            )
            return Response(content=twiml, media_type="application/xml")

        print(f"\n📩 [{profile_name or user_phone}]: {message_body}")

        # Get or create user
        db = request.app.state.db
        memory = request.app.state.memory
        action_router = request.app.state.action_router

        db.get_or_create_user(user_phone)

        # Step 1: Detect intent
        intent_data = detect_intent(message_body)
        print(f"   🎯 Intent: {intent_data['intent']} (confidence: {intent_data['confidence']})")

        # Step 2: If low confidence, use GPT for classification
        if intent_data["confidence"] < 0.3 and intent_data["intent"] == "general":
            ai_service = request.app.state.ai_service
            gpt_intent = await ai_service.classify_intent(message_body)
            if gpt_intent in ["reminder", "task_create", "task_complete", "task_list",
                              "summarize", "weather", "help", "greeting"]:
                intent_data["intent"] = gpt_intent
                intent_data["confidence"] = 0.7
                print(f"   🤖 GPT reclassified: {gpt_intent}")

        # Step 3: Save user message to memory
        memory.add_message(user_phone, "user", message_body, intent_data["intent"])

        # Step 4: Route to appropriate action handler
        response_text = await action_router.route(user_phone, message_body, intent_data)

        # Step 5: Save assistant response to memory
        memory.add_message(user_phone, "assistant", response_text)

        # Step 6: Log agent activity
        db.log_action(user_phone, f"intent_{intent_data['intent']}", message_body[:200])

        print(f"   📤 Response: {response_text[:100]}...")

        # Return TwiML response
        twiml = WhatsAppService.create_twiml_response(response_text)
        return Response(content=twiml, media_type="application/xml")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        twiml = WhatsAppService.create_twiml_response(
            "⚠️ Sorry, something went wrong. Please try again!"
        )
        return Response(content=twiml, media_type="application/xml")


# ─── Simulator Endpoint (for testing without Twilio) ─────────────

@app.post("/api/simulate")
async def simulate_message(request: Request):
    """Simulate a WhatsApp message for testing purposes."""
    try:
        data = await request.json()
        user_phone = data.get("phone", "whatsapp:+1234567890")
        message_body = data.get("message", "")

        if not message_body:
            raise HTTPException(status_code=400, detail="Message is required")

        db = request.app.state.db
        memory = request.app.state.memory
        action_router = request.app.state.action_router

        db.get_or_create_user(user_phone)

        # Detect intent
        intent_data = detect_intent(message_body)

        # Use GPT fallback if needed
        if intent_data["confidence"] < 0.3 and intent_data["intent"] == "general":
            ai_service = request.app.state.ai_service
            gpt_intent = await ai_service.classify_intent(message_body)
            if gpt_intent != "general":
                intent_data["intent"] = gpt_intent
                intent_data["confidence"] = 0.7

        # Save and process
        memory.add_message(user_phone, "user", message_body, intent_data["intent"])
        response_text = await action_router.route(user_phone, message_body, intent_data)
        memory.add_message(user_phone, "assistant", response_text)
        db.log_action(user_phone, f"sim_{intent_data['intent']}", message_body[:200])

        return {
            "response": response_text,
            "intent": intent_data["intent"],
            "confidence": intent_data["confidence"],
            "entities": intent_data["entities"]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Dashboard API Endpoints ─────────────────────────────────────

@app.get("/api/stats")
async def get_stats(request: Request):
    """Get dashboard statistics."""
    db = request.app.state.db
    return db.get_stats()


@app.get("/api/users")
async def get_users(request: Request):
    """Get all users."""
    db = request.app.state.db
    return db.get_all_users()


@app.get("/api/conversations")
async def get_conversations(request: Request, limit: int = 50, user_phone: Optional[str] = None):
    """Get recent conversations."""
    db = request.app.state.db
    if user_phone:
        return db.get_conversation_history(user_phone, limit)
    return db.get_all_conversations(limit)


@app.get("/api/reminders")
async def get_reminders(request: Request, status: Optional[str] = None, user_phone: Optional[str] = None):
    """Get reminders."""
    db = request.app.state.db
    return db.get_reminders(user_phone=user_phone, status=status)


@app.get("/api/tasks")
async def get_tasks(request: Request, status: Optional[str] = None, user_phone: Optional[str] = None):
    """Get tasks."""
    db = request.app.state.db
    return db.get_tasks(user_phone=user_phone, status=status)


@app.get("/api/logs")
async def get_agent_logs(request: Request, limit: int = 50):
    """Get agent activity logs."""
    db = request.app.state.db
    return db.get_agent_logs(limit)


# ─── Run Server ──────────────────────────────────────────────────

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=Config.DEBUG,
        log_level="info"
    )

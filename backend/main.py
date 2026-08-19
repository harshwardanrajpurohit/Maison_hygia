import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from backend.data.products import get_all_products, get_product_by_id
from backend.conversation import ConversationManager
from backend.models import UserProfile

app = FastAPI(title="Maison Hygia Ritual Intelligence API")

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

conv_manager = ConversationManager()

# Mock Analytics Store
mock_analytics = {
    "conversations_started": 0,
    "rituals_completed": 0,
    "safety_triggered": 0,
    "modifications_requested": 0
}

# Resolve frontend directory path
BACKEND_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"

class MessageRequest(BaseModel):
    conversation_id: str
    message: str

# ── API Routes ──────────────────────────────────────────────

@app.post("/api/conversation/start")
def start_conversation():
    import uuid
    conv_id = str(uuid.uuid4())
    mock_analytics["conversations_started"] += 1
    return conv_manager.start_conversation(conv_id)

@app.post("/api/conversation/message")
async def send_message(request: Request):
    """
    Accepts either:
      - application/json  with {conversation_id, message}
      - multipart/form-data with conversation_id, message, and optional image file
    """
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        data = await request.json()
        c_id = data.get("conversation_id", "")
        msg = data.get("message", "")
        if not c_id:
            raise HTTPException(status_code=400, detail="conversation_id is required")
    else:
        # multipart/form-data path
        form = await request.form()
        c_id = form.get("conversation_id", "")
        msg = form.get("message", "")

        if not c_id:
            raise HTTPException(status_code=400, detail="conversation_id is required")

    image_data = None
    image_type = None
    if "multipart/form-data" in content_type:
        image_file: UploadFile = form.get("image")
        if image_file and hasattr(image_file, "read"):
            image_data = await image_file.read()
            image_type = image_file.content_type

    # Update Analytics
    msg_lower = str(msg).lower()
    if "simpler" in msg_lower or "more hydration" in msg_lower or "more relaxation" in msg_lower:
        mock_analytics["modifications_requested"] += 1

    result = conv_manager.process_message(str(c_id), str(msg), image_data, image_type)
    
    if result.get("safety_status") == "MEDICAL_RISK":
        mock_analytics["safety_triggered"] += 1
    if result.get("ritual"):
        mock_analytics["rituals_completed"] += 1
        
    return result

@app.get("/api/products")
def list_products():
    return [p.model_dump() for p in get_all_products()]

@app.get("/api/analytics")
def get_analytics():
    return mock_analytics

# ── Static File Serving ─────────────────────────────────────

@app.get("/")
def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")

# Mount frontend static assets (CSS, JS) — must come AFTER API routes
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

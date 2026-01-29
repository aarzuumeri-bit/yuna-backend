from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import ChatRequest, ChatResponse
from .llm import call_llm
from .database import db
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Yuna Backend")

# 🔥 CORS FIX — THIS IS THE KEY
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for development ONLY
    allow_credentials=True,
    allow_methods=["*"],  # allows OPTIONS, POST, etc.
    allow_headers=["*"],
)

# ===== SCHEMAS =====

class CreateChatRequest(BaseModel):
    id: str
    title: str

class UpdateChatRequest(BaseModel):
    title: str

class AddMessageRequest(BaseModel):
    chat_id: str
    role: str
    content: str

# ===== ENDPOINTS =====

@app.get("/health")
def health():
    return {"status": "ok", "assistant": "Yuna"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        # Debug: Print the received mode
        print(f"🎭 Received mode: {request.mode}")
        reply = call_llm(request.messages, mode=request.mode)
        return ChatResponse(reply=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== CHAT MANAGEMENT =====

@app.get("/chats")
def get_all_chats():
    """Get all chats"""
    try:
        chats = db.get_all_chats()
        return {"chats": chats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chats")
def create_chat(request: CreateChatRequest):
    """Create a new chat"""
    try:
        chat = db.create_chat(request.id, request.title)
        print(f"✅ Created chat: {request.title} (ID: {request.id})")
        return chat
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chats/{chat_id}")
def get_chat(chat_id: str):
    """Get a specific chat with all messages"""
    try:
        chat = db.get_chat_with_messages(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/chats/{chat_id}")
def update_chat(chat_id: str, request: UpdateChatRequest):
    """Update chat title"""
    try:
        success = db.update_chat_title(chat_id, request.title)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        print(f"✏️ Renamed chat {chat_id} to: {request.title}")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/chats/{chat_id}")
def delete_chat(chat_id: str):
    """Delete a chat"""
    try:
        success = db.delete_chat(chat_id)
        if not success:
            raise HTTPException(status_code=404, detail="Chat not found")
        print(f"🗑️ Deleted chat: {chat_id}")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== MESSAGE MANAGEMENT =====

@app.post("/messages")
def add_message(request: AddMessageRequest):
    """Add a message to a chat"""
    try:
        message = db.add_message(request.chat_id, request.role, request.content)
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chats/{chat_id}/messages")
def get_chat_messages(chat_id: str):
    """Get all messages for a chat"""
    try:
        messages = db.get_chat_messages(chat_id)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

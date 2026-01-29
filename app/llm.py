import os
import subprocess
import requests
import json
from typing import List, Optional
from dotenv import load_dotenv
from .prompt import SYSTEM_PROMPT, MODE_PROMPTS
from .schemas import Message

# Load env variables
load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OLLAMA_MODEL = "mistral"

def call_llm(messages: List[Message], mode: Optional[str] = None) -> str:
    """Dispatches call to the configured provider"""
    if PROVIDER == "gemini":
        return call_gemini(messages, mode)
    return call_ollama(messages, mode)

def call_gemini(messages: List[Message], mode: Optional[str] = None) -> str:
    if not GOOGLE_API_KEY or "your_api_key" in GOOGLE_API_KEY:
        return "System Error: GOOGLE_API_KEY is missing in backend .env file."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GOOGLE_API_KEY}"
    
    # Prepare System Prompt
    sys_text = SYSTEM_PROMPT
    if mode and mode in MODE_PROMPTS:
        sys_text += f"\n\n🚨 IMPORTANT MODE INSTRUCTION:\n{MODE_PROMPTS[mode]}"

    # Convert History
    contents = []
    for msg in messages:
        role = "user" if msg.role == "user" else "model"
        contents.append({
            "role": role, 
            "parts": [{"text": msg.content}]
        })

    payload = {
        "systemInstruction": {
            "parts": [{"text": sys_text}]
        },
        "contents": contents
    }

    try:
        response = requests.post(
            url, 
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            return f"Gemini API Error {response.status_code}: {response.text}"
            
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            candidate = data["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                return candidate["content"]["parts"][0]["text"].strip()
            return "No content generated."
        return "Error: Empty response from Gemini."

    except Exception as e:
        return f"Gemini Network Error: {str(e)}"

def call_ollama(messages: List[Message], mode: Optional[str] = None) -> str:
    # Start with system prompt
    prompt_parts = [SYSTEM_PROMPT, ""]
    
    # Add conversation history
    for msg in messages:
        if msg.role == "user":
            prompt_parts.append(f"User: {msg.content}")
        else:
            prompt_parts.append(f"Assistant: {msg.content}")

    # Add mode-specific instructions RIGHT BEFORE the assistant response
    if mode and mode in MODE_PROMPTS:
        prompt_parts.append("")
        prompt_parts.append("=" * 60)
        prompt_parts.append("⚠️ IMPORTANT - CURRENT MODE INSTRUCTION ⚠️")
        prompt_parts.append("=" * 60)
        prompt_parts.append(MODE_PROMPTS[mode])
        prompt_parts.append("=" * 60)
        prompt_parts.append("YOU MUST FOLLOW THE ABOVE MODE INSTRUCTION IN YOUR NEXT RESPONSE!")
        prompt_parts.append("=" * 60)
        prompt_parts.append("")

    prompt_parts.append("Assistant:")
    final_prompt = "\n".join(prompt_parts)

    try:
        result = subprocess.run(
            ["ollama", "run", OLLAMA_MODEL],
            input=final_prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
        )
        if result.returncode != 0:
            return f"Ollama Error: {result.stderr}"
        
        return result.stdout.strip()
    except Exception as e:
        return f"Local Inference Error: {str(e)}"

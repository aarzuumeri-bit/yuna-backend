import os
import subprocess
from typing import List, Optional
from dotenv import load_dotenv
from .prompt import SYSTEM_PROMPT, MODE_PROMPTS
from .schemas import Message

# Load env variables
load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
OLLAMA_MODEL = "mistral"
GEMINI_MODEL = "gemini-1.5-flash"

# Configure Gemini if active
genai = None
if PROVIDER == "gemini":
    try:
        import google.generativeai as genai
        if GOOGLE_API_KEY:
            genai.configure(api_key=GOOGLE_API_KEY)
    except ImportError:
        print("⚠️ Warning: google-generative-ai not installed. Gemini mode will fail.")

def call_llm(messages: List[Message], mode: Optional[str] = None) -> str:
    """Dispatches call to the configured provider"""
    if PROVIDER == "gemini":
        if genai is None:
            return "Configuration Error: google-generative-ai library not found."
        return call_gemini(messages, mode)
    return call_ollama(messages, mode)

def call_gemini(messages: List[Message], mode: Optional[str] = None) -> str:
    if not GOOGLE_API_KEY or "your_api_key" in GOOGLE_API_KEY:
        return "System Error: GOOGLE_API_KEY is missing in backend .env file."

    try:
        # Prepare System Prompt with Mode
        system_instruction = SYSTEM_PROMPT
        if mode and mode in MODE_PROMPTS:
            system_instruction += f"\n\n🚨 IMPORTANT MODE INSTRUCTION:\n{MODE_PROMPTS[mode]}"

        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            system_instruction=system_instruction
        )

        # Convert History
        # Gemini expects alternating user/model. We must ensure structure.
        formatted_history = []
        for msg in messages:
            role = "user" if msg.role == "user" else "model"
            formatted_history.append({"role": role, "parts": [msg.content]})

        response = model.generate_content(formatted_history)
        return response.text.strip()
    except Exception as e:
        return f"Gemini Cloud Error: {str(e)}"

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

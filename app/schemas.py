from pydantic import BaseModel
from typing import List, Literal, Optional

class Message(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    mode: Optional[str] = None  # Accept mode but make it optional

class ChatResponse(BaseModel):
    reply: str

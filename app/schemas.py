from typing import Literal
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    role: Literal["system","user","assistant"]
    content: str = Field(min_length=1)

class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    temperature: float = Field(default=0.2,ge=0,le=2)

class ChatResponse(BaseModel):
    answer: str


class TaskExtractRequest(BaseModel):
    text: str = Field(min_length=1)

class ExtractedTask(BaseModel):
    intent: Literal["question","todo","email","bug_report","unknown"]
    summary: str 
    priority: Literal["low","medium","high"]
    needs_tool:bool
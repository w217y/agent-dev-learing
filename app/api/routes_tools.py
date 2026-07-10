

from fastapi import APIRouter
from app.llm import chat_completion
from app.schemas import ChatRequest,ChatResponse

router = APIRouter(prefix="/api",tags=["tools"])

@router.post("/tool-chat",response_model=ChatResponse)
async def tool_chat(request: ChatRequest):
    messages = [m.model_dump() for m in request.messages]
    answer = chat_completion(messages,temperature=request.temperature)
    return ChatResponse(answer=answer)
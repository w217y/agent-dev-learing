import time

from fastapi import APIRouter
from app.llm import chat_completion
from fastapi.responses import StreamingResponse
from app.schemas import ChatRequest,ChatResponse

router = APIRouter(prefix="/api",tags=["chat"])

def fake_stream_text(text: str):
    for char in text:
        yield char
        time.sleep(0.01)

@router.post("/chat",response_model=ChatResponse)
async def chat(request: ChatRequest):
    messages = [m.model_dump() for m in request.messages]
    answer = chat_completion(messages,temperature=request.temperature)
    return ChatResponse(answer=answer)


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    messages = [m.model_dump() for m in request.messages]
    answer = chat_completion(messages,temperature=request.temperature)
    return StreamingResponse(
        fake_stream_text(answer),
        media_type="text/plain"
    )


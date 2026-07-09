from fastapi import APIRouter
from app.schemas import TaskExtractRequest,ExtractedTask
from app.llm import extract_task

router = APIRouter()

@router.post("/extract_task",response_model=ExtractedTask)
async def extract_task_route(request: TaskExtractRequest):
    return extract_task(request.text)
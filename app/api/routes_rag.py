from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.rag.retriever import retrieve, retrieve_with_debug
from app.rag.generator import generate_rag_answer


router = APIRouter(prefix="/api/rag",tags=["rag"])

class RagQueryRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = 5
    min_score: float | None = Field(default=None, ge=-1, le=1)

@router.post("/retrieve")
async def retrieve_route(request: RagQueryRequest):
    chunks = retrieve(request.question, top_k=request.top_k)
    return {"chunks":chunks}


@router.post("/query")
async def rag_query(request: RagQueryRequest):
    result = retrieve_with_debug(
        request.question,
        top_k=request.top_k,
        min_score=request.min_score,
    )

    chunks = result["chunks"]

    if not chunks:
        return {
            "answer": "根据当前知识库资料，无法确认。",
            "sources": [],
            "debug": result["debug"],
        }

    answer = generate_rag_answer(request.question, chunks)

    sources = [
        {
            "filename": chunk["filename"],
            "source": chunk["source"],
            "score": chunk["score"],
        } for chunk in chunks
    ]

    return {
        "answer": answer,
        "sources": sources,
        "debug": result["debug"],
    }
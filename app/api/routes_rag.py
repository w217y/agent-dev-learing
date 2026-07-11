from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.rag.retriever import retrieve
from app.rag.generator import generate_rag_answer

MIN_RAG_SCORE = 0.45


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
    chunks = retrieve(request.question, top_k=request.top_k)

    min_score = request.min_score if request.min_score is not None else MIN_RAG_SCORE
    relevant_chunks = [
        chunk for chunk in chunks
        if chunk["score"] if not None and chunk["score"] >= min_score
    ]

    if not relevant_chunks:
        return {
        "answer": "根据当前知识库资料，无法确认。",
        "sources": [],
        "debug": {
            "min_score": min_score,
            "retrieved_count": len(chunks),
            "max_score": max([chunk["score"] for chunk in chunks], default=None),
        },
    }

    answer = generate_rag_answer(request.question, chunks)

    sources = [
        {
            "filename": chunk["filename"],
            "source": chunk["source"],
            "score": chunk["score"],
        } for chunk in relevant_chunks
    ]

    return {
        "answer": answer,
        "sources": sources,
        "debug": {
            "min_score": min_score,
            "retrieved_count": len(chunks),
            "used_count": len(relevant_chunks),
            "max_score": max([chunk["score"] for chunk in chunks], default=None),
        },
    }
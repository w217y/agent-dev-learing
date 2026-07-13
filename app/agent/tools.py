from app.rag.retriever import retrieve
from app.rag.generator import generate_rag_answer

def vector_search_tool(question: str, top_k: int = 5) -> dict:
    chunks = retrieve(question,top_k)

    if not chunks:
        return {
            "answer": "根据当前知识库资料，无法确认",
            "sources": [],
        }
    
    answer = generate_rag_answer(question, chunks)

    sources = [
        {
            "filename": chunk["filename"],
            "source": chunk["source"],
            "score": chunk["score"],
        }
        for chunk in chunks
    ]

    return{
        "answer": answer,
        "sources":sources,
    }
    
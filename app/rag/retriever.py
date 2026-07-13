from sqlalchemy import text

from app.config import settings

from app.db.session import engine
from app.rag.embeddings import embed_query

def similarity_search(query: str, top_k: int | None = None) -> list[dict]:
    top_k = top_k or settings.top_k
    query_embedding = embed_query(query)

    with engine.begin() as conn:
        rows = conn.execute(
            text("""
            SELECT
                dc.id,
                dc.document_id,
                d.filename,
                dc.chunk_index,
                dc.content,
                dc.source,
                1 - (dc.embedding <=> :query_embedding) AS score
            FROM document_chunks dc
            JOIN documents d ON dc.document_id = d.id
            ORDER BY dc.embedding <=> :query_embedding
            LIMIT :top_k
            """),
            {
                "query_embedding": str(query_embedding),
                "top_k": top_k,
            },
        ).mappings().all()

    return [dict(row) for row in rows]

def filter_relevant_chunks(chunks: list[dict], min_score: float) -> list[dict]:

    return[
        chunk
        for chunk in chunks
        if chunk.get("score") is not None and chunk["score"] >= min_score
    ]


def retrieve(
    query:str,
    top_k: int | None = None,
    min_score: float | None = None,
) -> list[dict]:
    min_score = min_score if min_score is not None else settings.min_rag_score
    raw_chunks = similarity_search(query,top_k=top_k)
    return filter_relevant_chunks(raw_chunks,min_score=min_score)
    
    
def retrieve_with_debug(
        query: str,
        top_k: int | None=None,
        min_score: float | None=None,
) -> dict:
    """API 调试或 eval 使用：同时返回 raw/relevant/debug。"""
    min_score = min_score if min_score is not None else settings.min_rag_score
    raw_chunks = similarity_search(query, top_k=top_k)
    relevant_chunks = filter_relevant_chunks(raw_chunks, min_score=min_score)

    return {
        "chunks": relevant_chunks,
        "debug": {
            "min_score": min_score,
            "retrieved_count": len(raw_chunks),
            "used_count": len(relevant_chunks),
            "max_score": max([chunk["score"] for chunk in raw_chunks], default=None),
        },
    }

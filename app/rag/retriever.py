from sqlalchemy import text
from app.db.session import engine
from app.rag.embeddings import embed_query

from app.config import settings

def retrieve(query: str,top_k: int | None = None) -> list[dict]:
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


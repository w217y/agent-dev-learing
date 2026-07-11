from sqlalchemy import text

from app.config import settings
from app.db.session import engine

def init_db():
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'uploaded',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )  
        """))

        conn.execute(text(f"""
        CREATE TABLE IF NOT EXISTS document_chunks (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            token_count INTEGER,
            source TEXT,
            embedding vector({settings.embedding_dim}),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """))

        conn.execute(text("""
        CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx
        ON document_chunks
        USING ivfflat (embedding vector_cosine_ops)
        WITH (lists = 100)
        """))
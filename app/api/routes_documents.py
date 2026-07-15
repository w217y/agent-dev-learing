import os

from fastapi import APIRouter, UploadFile, File, HTTPException

from sqlalchemy import text

from app.config import settings
from app.db.session import engine

from app.rag.loaders import load_document
from app.rag.chunking import split_text
from app.rag.embeddings import embed_texts
from app.core.security import validate_file_type

router = APIRouter(prefix="/api/documents",tags=["documents"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    try:
        validate_file_type(file.filename)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    os.makedirs(settings.upload_dir,exist_ok=True)

    file_path = os.path.join(settings.upload_dir,file.filename)

    with open(file_path,"wb") as f:
        f.write(await file.read())

    file_type = file.filename.split(".")[-1].lower()

    with engine.begin() as conn:
        result = conn.execute(
            text("""
            INSERT INTO documents (filename,file_type,
                                file_path,status)
            VALUES (:filename, :file_type, :file_path,'uploaded')
            RETURNING id     
            """), 
            {
                "filename": file.filename,
                "file_path": file_path,
                "file_type": file_type,
            },
        )
        document_id = result.scalar_one()

    return {
        "document_id": document_id,
        "filename": file.filename,
        "file_type": file_type,
        "file_path": file_path,
        "status": "uploaded",
    }
        
@router.post("/ingest/{document_id}")
async def ingest_document(document_id: int):
    with engine.begin() as conn:
        doc = conn.execute(
            text("SELECT * FROM documents WHERE id = :id"),
            {"id":document_id},
        ).mappings().first()

        if not doc:
            raise HTTPException(status_code=404,detail="document not found")

    try:
        raw_text = load_document(doc["file_path"],doc["file_type"])
    except ValueError as e:   
        raise HTTPException(status_code=400,detail=str(e))

    chunks = split_text(raw_text)

    if not chunks:
        raise HTTPException(status_code=400,detail="document has no readable text")

    embeddings = embed_texts(chunks)

    with engine.begin() as conn:
        conn.execute(
            text("DELETE FROM document_chunks WHERE document_id = :document_id"),
            {"document_id": document_id},
        )

        for idx, (chunk, embedding) in enumerate(zip(chunks,embeddings)):
            conn.execute(
                text("""
                INSERT INTO document_chunks
                (document_id,chunk_index,content,token_count,source,embedding)
                VALUES
                (:document_id, :chunk_index, :content, :token_count, :source, :embedding)
                """),
                {
                    "document_id": document_id,
                    "chunk_index": idx,
                    "content": chunk,
                    "token_count": len(chunk),
                    "source": f"{doc['filename']}#chunk-{idx}",
                    "embedding": embedding,
                }
            )
        conn.execute(
            text("UPDATE documents SET status = 'indexed' WHERE id = :id"),
            {"id":document_id},
        )

    return {
        "document_id": document_id,
        "chunks": len(chunks),
        "embedding_provider": settings.embedding_provider,
        "embedding_model": settings.embedding_model,
        "embedding_dim": settings.embedding_dim,
        "status": "indexed",
    }

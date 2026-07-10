import os

from fastapi import APIRouter, UploadFile, File

from sqlalchemy import text

from app.config import settings
from app.db.session import engine

router = APIRouter(prefix="/api/documents",tags=["documents"])

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
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
        "ducument_id": document_id,
        "filename": file.filename,
        "file_type": file_type,
        "file_path": file_path,
        "status": "uploaded",
    }
        
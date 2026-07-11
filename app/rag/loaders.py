from pathlib import Path
from pypdf import PdfReader


def load_txt(path:str)->str:
    return Path(path).read_text(encoding="utf-8")


def load_markdown(path:str)->str:
    return Path(path).read_text(encoding="utf-8")


def load_pdf(path: str) -> str:
    reader = PdfReader(path)
    pages = []

    for i , page in enumerate(reader.pages):
        text = page.extract_text or ""
        pages.append(f"\n\n[page{i+1}]\n{text}")

    return "\n".join(pages)


def load_document(file:str,file_type:str)->str:
    if file_type == "txt":
        return load_txt(file)
    
    if file_type in ["md","markdown"]:
        return load_markdown(file)
    
    if file_type == "pdf":
        return load_pdf(file)
    
    raise ValueError(f"Unsupported file type: {file_type}")
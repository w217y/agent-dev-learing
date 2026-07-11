import re

def clean_text(text: str)->str:
    text = re.sub(r"\n{3,}","\n\n",text)
    text = re.sub(r"[ \t]+", " ",text)

    return text.strip()

def split_text(text: str,chunk_size: int = 800, overlap: int = 120) -> list[str]:
    text = clean_text(text)

    chunks=[]
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - overlap

        if start < 0:
            start = 0
        
        if start >= len(text):
            break

    return chunks

        


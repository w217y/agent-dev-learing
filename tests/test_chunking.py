from app.rag.chunking import split_text

def test_split_text():
    text = "a" * 2000
    chunks = split_text(text,chunk_size=800,overlap=100)

    assert len(chunks) >= 3
    assert all(len(chunk) <= 800 for chunk in chunks)


    
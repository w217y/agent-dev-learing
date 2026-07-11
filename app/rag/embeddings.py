from functools import lru_cache

from sentence_transformers import SentenceTransformer

from app.config import settings

@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(
        settings.embedding_model,
        device=settings.embedding_device,
    )

def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    
    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        normalize_embeddings= True,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    return embeddings.tolist()

def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]
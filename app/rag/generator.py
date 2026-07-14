# from openai import OpenAI
from langfuse.openai import openai
from app.config import settings
from app.rag.prompts import RAG_SYSTEM_PROMPT

client = openai.OpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_api_base_url,
)

def build_context(chunks: list[dict]) -> str:
    parts = []

    for chunk in chunks:
        parts.append(
            f"[来源：{chunk['source']}]\n{chunk['content']}"
        )
    
    return "\n\n---\n\n".join(parts)

def generate_rag_answer(question: str, chunks: list[dict])-> str:
    context = build_context(chunks)

    response = client.responses.create(
        model=settings.openai_model,
        input=[
            {
                "role": "system",
                "content": RAG_SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": f"[问题]\n{question}\n\n[参考资料]\n{context}",
            },
        ],
        temperature = 0.1,
    )

    return response.output_text
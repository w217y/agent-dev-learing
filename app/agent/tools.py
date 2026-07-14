import uuid
from datetime import datetime

from app.rag.retriever import retrieve
from app.rag.generator import generate_rag_answer

from sqlalchemy import text
from app.db.session import engine

SAFE_SQL_MAP = {
    "list_vip_customers": """
        SELECT id, name, level, city
        FROM customers
        WHERE level = 'VIP'
    """,
    "list_pending_orders": """
        SELECT o.id, c.name AS customer_name, o.amount, o.status
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.status = 'pending'
    """,
}

def sql_query_tool(query_name: str) -> dict:
    if query_name not in SAFE_SQL_MAP:
        return {
            "error": "不支持的查询类型。只能执行预定义安全查询。",
        }
    
    sql = SAFE_SQL_MAP[query_name]

    with engine.begin() as conn:
        rows = conn.execute(text(sql)).mappings().all()

    return {
        "query_name": query_name,
        "rows": [dict(row) for row in rows],
    }


def vector_search_tool(question: str, top_k: int = 5) -> dict:
    chunks = retrieve(question,top_k)

    if not chunks:
        return {
            "answer": "根据当前知识库资料，无法确认",
            "sources": [],
        }
    
    answer = generate_rag_answer(question, chunks)

    sources = [
        {
            "filename": chunk["filename"],
            "source": chunk["source"],
            "score": chunk["score"],
        }
        for chunk in chunks
    ]

    return{
        "answer": answer,
        "sources":sources,
    }
    
def create_ticket_draft_tool(title: str, description: str, priority: str = "medium") -> dict:
    return {
        "draft_id": str(uuid.uuid4()),
        "type": "ticket",
        "title": title,
        "description": description,
        "priority": priority,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "status": "draft",
    }

def draft_email_tool(to: str, subject: str, body: str) -> dict:
    return {
        "draft_id": str(uuid.uuid4()),
        "type": "email",
        "to": to,
        "subject": subject,
        "body": body,
        "status": "draft",
    }
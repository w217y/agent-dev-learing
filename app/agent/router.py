
from typing import Literal
from pydantic import BaseModel, Field
# from openai import OpenAI

from app.config import settings
from app.agent.prompts import ROUTER_SYSTEM_PROMPT
from langfuse.openai import openai

client = openai.OpenAI(
    api_key=settings.openai_api_key,
    base_url=settings.openai_api_base_url,
    timeout=settings.llm_timeout_seconds,
)

class RouteDecision(BaseModel):
    intent: Literal[
        "rag_query",
        "sql_query",
        "create_ticket",
        "draft_email",
        "smalltalk",
    ]
    reason: str = Field(description="为什么选择这个 intent")
    confidence: float = Field(ge=0, le=1)

def classify_by_keywords(user_input: str) -> str:
    """LLM Router 失败时的兜底关键词路由。动作优先于主题。"""

    if "工单" in user_input:
        return "create_ticket"

    if "邮件" in user_input:
        return "draft_email"

    if "订单" in user_input or "客户" in user_input:
        return "sql_query"

    if "报销" in user_input or "制度" in user_input:
        return "rag_query"

    return "smalltalk"

def classify_intent(user_input: str) -> RouteDecision:
    try:
        response = client.responses.parse(
            model=settings.openai_model,
            input=[
                {
                    "role": "system",
                    "content": ROUTER_SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content":user_input,
                },
            ],
            text_format=RouteDecision
        )
        decision = response.output_parsed

        if decision.confidence < 0.5:
            return RouteDecision(
                intent="smalltalk",
                reason=f"LLM router confidence too low: {decision.reason}",
                confidence=decision.confidence,
            )
        
        return decision
    
    except Exception as exc:
        fallback_intent = classify_by_keywords(user_input)

        return RouteDecision(
            intent=fallback_intent,
            reason=f"LLM router failed: {exc}. Used keyword fallback.",
            confidence=0.3,
        )


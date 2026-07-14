from types import SimpleNamespace

from app.agent import router
from app.agent.router import (
    RouteDecision,
    classify_by_keywords,
    classify_intent,
)
from app.agent.prompts import ROUTER_SYSTEM_PROMPT


def test_router_prompt_contains_priority_rule():
    """Router prompt 必须包含动作优先规则。"""

    assert "动作优先于主题" in ROUTER_SYSTEM_PROMPT
    assert "创建工单" in ROUTER_SYSTEM_PROMPT
    assert "写邮件" in ROUTER_SYSTEM_PROMPT


def test_keyword_router_ticket_with_reimbursement_topic():
    """工单 + 报销：工单是动作，报销是主题，应识别为 create_ticket。"""

    intent = classify_by_keywords("帮我创建一个工单，说明报销资料缺失")

    assert intent == "create_ticket"


def test_keyword_router_email_with_reimbursement_topic():
    """邮件 + 报销：邮件是动作，报销是主题，应识别为 draft_email。"""

    intent = classify_by_keywords("帮我给财务写一封邮件，说明报销资料已经补齐")

    assert intent == "draft_email"


def test_keyword_router_rag_policy_question():
    """单纯询问报销制度，应识别为 rag_query。"""

    intent = classify_by_keywords("报销需要哪些材料？")

    assert intent == "rag_query"


def test_keyword_router_sql_customer_question():
    """查询客户/订单等结构化数据，应识别为 sql_query。"""

    intent = classify_by_keywords("帮我查一下 VIP 客户有哪些")

    assert intent == "sql_query"


def test_classify_intent_success_uses_valid_message_roles(monkeypatch):
    """
    测试 LLM Router 请求格式。

    这个测试主要防止你之前遇到的错误：
    Invalid value: ''. Supported values are: assistant/system/developer/user
    """

    def fake_parse(**kwargs):
        input_messages = kwargs["input"]

        assert input_messages[0]["role"] == "system"
        assert input_messages[0]["content"] == ROUTER_SYSTEM_PROMPT

        assert input_messages[1]["role"] == "user"
        assert input_messages[1]["content"] == "帮我创建一个工单，说明报销资料缺失"

        assert kwargs["text_format"] is RouteDecision

        return SimpleNamespace(
            output_parsed=RouteDecision(
                intent="create_ticket",
                reason="用户明确要求创建工单，报销资料缺失只是工单描述内容。",
                confidence=0.95,
            )
        )

    monkeypatch.setattr(router.client.responses, "parse", fake_parse)

    decision = classify_intent("帮我创建一个工单，说明报销资料缺失")

    assert decision.intent == "create_ticket"
    assert "创建工单" in decision.reason
    assert decision.confidence == 0.95


def test_classify_intent_fallback_when_llm_fails(monkeypatch):
    """LLM Router 失败时，应回退到关键词路由，而不是固定 smalltalk。"""

    def fake_parse(**kwargs):
        raise RuntimeError("mock upstream error")

    monkeypatch.setattr(router.client.responses, "parse", fake_parse)

    decision = classify_intent("帮我创建一个工单，说明报销资料缺失")

    assert decision.intent == "create_ticket"
    assert decision.confidence > 0
    assert "fallback" in decision.reason.lower() or "关键词" in decision.reason

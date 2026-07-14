from app.agent import nodes
from app.agent.graph import agent_graph
from app.agent.router import RouteDecision


def test_agent_graph_routes_to_ticket_with_router_reason(monkeypatch):
    """工单 + 报销冲突样例：应该走 ticket_draft，而不是 rag 或 smalltalk。"""

    def fake_classify_intent(user_input: str) -> RouteDecision:
        return RouteDecision(
            intent="create_ticket",
            reason="用户明确要求创建工单，报销资料缺失只是工单描述内容。",
            confidence=0.96,
        )

    monkeypatch.setattr(nodes, "classify_intent", fake_classify_intent)

    result = agent_graph.invoke({
        "user_input": "帮我创建一个工单，说明报销资料缺失",
        "steps": [],
    })

    assert result["intent"] == "create_ticket"
    assert result["router_reason"] == "用户明确要求创建工单，报销资料缺失只是工单描述内容。"
    assert result["router_confidence"] == 0.96

    assert result["tool_name"] == "create_ticket_draft_tool"
    assert result["approval_required"] is True
    assert result["approval_status"] == "pending"
    assert result["pending_action"]["type"] == "ticket"

    assert result["steps"] == [
        "router:create_ticket",
        "ticket_draft",
        "final",
    ]


def test_agent_graph_routes_to_email_with_router_reason(monkeypatch):
    """邮件 + 报销冲突样例：应该走 email_draft。"""

    def fake_classify_intent(user_input: str) -> RouteDecision:
        return RouteDecision(
            intent="draft_email",
            reason="用户明确要求写邮件，报销资料补齐只是邮件正文内容。",
            confidence=0.93,
        )

    monkeypatch.setattr(nodes, "classify_intent", fake_classify_intent)

    result = agent_graph.invoke({
        "user_input": "帮我给财务写一封邮件，说明报销资料已经补齐",
        "steps": [],
    })

    assert result["intent"] == "draft_email"
    assert result["router_reason"] == "用户明确要求写邮件，报销资料补齐只是邮件正文内容。"
    assert result["router_confidence"] == 0.93

    assert result["tool_name"] == "draft_email_tool"
    assert result["approval_required"] is True
    assert result["approval_status"] == "pending"
    assert result["pending_action"]["type"] == "email"

    assert result["steps"] == [
        "router:draft_email",
        "email_draft",
        "final",
    ]


def test_agent_graph_routes_to_smalltalk(monkeypatch):
    """普通闲聊应该走 smalltalk。"""

    def fake_classify_intent(user_input: str) -> RouteDecision:
        return RouteDecision(
            intent="smalltalk",
            reason="用户只是普通问候，没有明确业务任务。",
            confidence=0.88,
        )

    monkeypatch.setattr(nodes, "classify_intent", fake_classify_intent)

    result = agent_graph.invoke({
        "user_input": "你好，你能做什么？",
        "steps": [],
    })

    assert result["intent"] == "smalltalk"
    assert result["router_reason"] == "用户只是普通问候，没有明确业务任务。"
    assert result["router_confidence"] == 0.88
    assert result["steps"] == [
        "router:smalltalk",
        "smalltalk",
        "final",
    ]
    assert "企业业务助手" in result["answer"]

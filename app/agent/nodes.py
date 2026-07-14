from app.agent.state import AgentState
from app.agent.router import classify_intent
from app.agent.tools import (
    vector_search_tool,
    sql_query_tool,
    create_ticket_draft_tool,
    draft_email_tool,
)


def router_node(state: AgentState) -> AgentState:
    decision = classify_intent(state["user_input"])

    return {
        **state,
        "intent": decision.intent,
        "router_reason": decision.reason,
        "router_confidence": decision.confidence,
        "steps": state.get("steps",[]) + [f"router:{decision.intent}"]
    }


def smalltalk_node(state: AgentState) -> AgentState:

    return {
        **state,
        "answer": "我是企业业务助手，可以帮你查知识库、查业务数据、生成工单草稿或邮件草稿。",
        "steps": state.get("steps", []) + ["smalltalk"],
    }

def final_node(state: AgentState) -> AgentState:
    return {
        **state,
        "steps": state.get("steps", []) + ["final"],
    }


def rag_node(state: AgentState)->AgentState:
    result = vector_search_tool(state["user_input"],top_k= 5)

    return {
        **state,
        "tool_name":"vector_search_tool",
        "tool_input": {"question": state["user_input"], "top_k": 5},
        "tool_result": result,
        "answer":result["answer"],
        "sources": result["sources"],
        "steps": state.get("steps", []) + ["rag"],
    }


def sql_node(state: AgentState) -> AgentState:
    user_input = state["user_input"]

    if "VIP" in user_input or "重要客户" in user_input:
        query_name = "list_vip_customers"
    elif "待支付" in user_input or "pending" in user_input or "未完成订单" in user_input:
        query_name = "list_pending_orders"
    else:
        query_name = "unknown"

    result = sql_query_tool(query_name)

    return {
        **state,
        "tool_name":"sql_query_tool",
        "tool_input":{"query_name":query_name},
        "tool_result":result,
        "answer": f"查询结果：{result}",
        "steps": state.get("steps", []) + ["sql"],
    }
    
def ticket_node(state: AgentState) -> AgentState:
    result = create_ticket_draft_tool(
        title="用户请求创建工单",
        description=state["user_input"],
        priority="medium",
    )

    return {
        **state,
        "tool_name": "create_ticket_draft_tool",
        "tool_result": result,
        "approval_required": True,
        "approval_status": "pending",
        "pending_action": result,
        "answer": "我已经生成工单草稿，请确认后再创建。",
        "steps": state.get("steps", []) + ["ticket_draft"],
    }

def email_node(state: AgentState) -> AgentState:
    result = draft_email_tool(
        to="finance@example.com",
        subject="事项说明",
        body=state["user_input"],
    )

    return {
        **state,
        "tool_name": "draft_email_tool",
        "tool_result": result,
        "approval_required": True,
        "approval_status": "pending",
        "pending_action": result,
        "answer": "我已经生成邮件草稿，请确认后再发送。",
        "steps": state.get("steps", []) + ["email_draft"],
    }


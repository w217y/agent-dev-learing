from app.agent.state import AgentState
from app.agent.tools import vector_search_tool


def router_node(state: AgentState) -> AgentState:
    user_input = state["user_input"]

    if "报销" in user_input or "制度" in user_input:
        intent = "rag_query"
    elif "订单" in user_input or "客户" in user_input:
        intent = "sql_query"
    elif "工单" in user_input:
        intent = "create_ticket"
    elif "邮件" in user_input:
        intent = "draft_email"
    else:
        intent = "smalltalk"

    return {
        **state,
        "intent": intent,
        "steps": state.get("steps",[]) + [f"router:{intent}"]
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
        "tool_input":{"qusetion":state["user_input"], "tok_5": 5},
        "tool_result": result,
        "answer":result["answer"],
        "sources": result["sources"],
        "steps": state.get("steps", []) + ["rag"],
    }
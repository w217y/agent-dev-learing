from langgraph.graph import StateGraph, START, END

from app.agent.state import AgentState
from app.agent.nodes import (
    router_node, 
    smalltalk_node, 
    final_node, 
    rag_node, 
    sql_node,
    ticket_node,
    email_node,
)

def route_after_router(state: AgentState) -> str:
    intent = state.get("intent","unknown")

    if intent == "rag_query":
        return "rag"
    if intent == "sql_query":
        return "sql"
    if intent == "create_ticket":
        return "ticket"
    if intent == "draft_email":
        return "email"
    
    return "smalltalk"

def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("rag",rag_node)
    graph.add_node("sql",sql_node)
    graph.add_node("ticket",ticket_node)
    graph.add_node("email",email_node)
    graph.add_node("smalltalk", smalltalk_node)
    graph.add_node("final", final_node)

    graph.add_edge(START, "router")

    graph.add_conditional_edges(
        "router",
        route_after_router,
        {
            "ticket": "ticket",
            "email": "email",
            "sql": "sql",
            "rag": "rag",
            "smalltalk": "smalltalk",
        },
    )
    
    graph.add_edge("ticket","final")
    graph.add_edge("email","final")
    graph.add_edge("sql","final")
    graph.add_edge("rag","final")
    graph.add_edge("smalltalk","final")
    graph.add_edge("final", END)

    return graph.compile()


agent_graph = build_agent_graph()
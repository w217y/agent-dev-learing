from langgraph.graph import StateGraph, START, END

from app.agent.state import AgentState
from app.agent.nodes import router_node, smalltalk_node, final_node

def route_after_router(state: AgentState) -> str:
    intent = state.get("intent","unknown")

    if intent == "smalltalk":
        return "smalltalk"
    
    return "smalltalk"

def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("router", router_node)
    graph.add_node("smalltalk", smalltalk_node)
    graph.add_node("final", final_node)

    graph.add_edge(START, "router")

    graph.add_conditional_edges(
        "router",
        route_after_router,
        {
            "smalltalk": "smalltalk",
        },
    )
    
    graph.add_edge("smalltalk","final")
    graph.add_edge("final", END)

    return graph.compile()


agent_graph = build_agent_graph()
from typing import Any, Literal
from typing_extensions import TypedDict

Intent = Literal[
    "rag_query",
    "sql_query",
    "create_ticket",
    "draft_email",
    "smalltalk",
    "unknown",
]

class AgentState(TypedDict, total=False):
    user_input: str
    intent: Intent

    # tool 
    tool_name: str
    tool_input: dict[str,Any]
    tool_result: dict[str, Any]

    #rag
    sources: list[dict[str, Any]]

    #approval
    approval_required: bool
    approval_status: Literal["pending","approved","rejected"]
    pending_action: dict[str, Any]

    #output
    answer: str
    error: str

    #observer
    steps: list[str]


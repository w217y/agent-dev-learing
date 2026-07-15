import logging
import uuid
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.agent.graph import agent_graph
from app.agent.memory import (
    save_run,
    get_run,
    update_run,
)
from app.core.security import validate_user_input

from app.core.tracing import trace_step

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agent",tags=["agent"])


class AgentChatRequest(BaseModel):
    message: str = Field(min_length=1)


class AgentApproveRequest(BaseModel):
    run_id: str
    approved: bool

@router.post("/chat")
async def agent_chat(request: AgentChatRequest):
    try:
        validate_user_input(request.message)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    
    run_id = str(uuid.uuid4())

    with trace_step(
        run_id,
        "agent_chat",
        metadata={"message": request.message}
    ):
        result = agent_graph.invoke({
            "user_input": request.message,
            "steps": [],
        })

    result["run_id"] = run_id
    save_run(run_id,result)

    logger.info(
        "agent_chat_completed",
        extra={
            "run_id": run_id,
            "steps": result.get("steps", []),
            "intent": result.get("intent"),
        },
    )

    return result

@router.post("/approve")
async def approve_action(request: AgentApproveRequest):
    state = get_run(request.run_id)

    if not state:
        raise HTTPException(status_code=400,detail="run not founud")
    
    if not state.get("approval_required"):
        return {
            "run_id": request.run_id,
            "message": "当前任务不需要审批。",
            "state": state,
        }
    
    if request.approved:
        state["approval_status"] = "approved"
        state["answer"] = "已确认。当前入门版将草稿标记为approved，暂不执行真实外部写操作。"
    else:
        state["approval_status"] = "rejected"
        state["answer"] = "已拒绝执行该操作"

    update_run(request.run_id,state)

    return {
        "run_id": request.run_id,
        "state": state,
    }

@router.get("/runs/{run_id}")
async def get_agent_run(run_id: str):

    state = get_run(run_id)

    if not state:
        raise HTTPException(status_code=404, detail="run not found")
    
    return state
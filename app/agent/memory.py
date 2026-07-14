from typing import Any

RUN_STORE: dict[str, dict[str, Any]] = {}

def save_run(run_id: str, state: dict[str, Any]) -> None:
    RUN_STORE[run_id] = state


def get_run(run_id: str) -> dict[str,  Any] | None:
    return RUN_STORE.get(run_id)


def update_run(run_id:str,state: dict[str,Any]) -> None:
    RUN_STORE[run_id] = state
import json

from app.agent.graph import agent_graph


def load_jsonl(path: str):
    with open(path, "r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue

            item = json.loads(line)
            validate_item(item, line_no)
            yield item


def validate_item(item: dict, line_no: int) -> None:
    required_fields = [
        "id",
        "user_input",
        "expected_intent",
        "expected_tool",
        "expected_approval_required",
        "expected_keywords",
        "purpose",
    ]

    for field in required_fields:
        if field not in item:
            raise ValueError(f"Line {line_no}: missing field {field}")

    if not isinstance(item["user_input"], str):
        raise ValueError(f"Line {line_no}: user_input must be str")

    if not isinstance(item["expected_intent"], str):
        raise ValueError(f"Line {line_no}: expected_intent must be str")

    if item["expected_tool"] is not None and not isinstance(item["expected_tool"], str):
        raise ValueError(f"Line {line_no}: expected_tool must be str or null")

    if not isinstance(item["expected_approval_required"], bool):
        raise ValueError(f"Line {line_no}: expected_approval_required must be bool")

    if not isinstance(item["expected_keywords"], list):
        raise ValueError(f"Line {line_no}: expected_keywords must be list[str]")


def main():
    total = 0
    intent_pass = 0
    tool_pass = 0
    approval_pass = 0

    for item in load_jsonl("evals/agent_tasks.jsonl"):
        total += 1

        result = agent_graph.invoke({
            "user_input": item["user_input"],
            "steps": [],
        })

        actual_intent = result.get("intent")
        actual_tool = result.get("tool_name")
        actual_approval_required = bool(result.get("approval_required", False))

        if actual_intent == item["expected_intent"]:
            intent_pass += 1

        if actual_tool == item["expected_tool"]:
            tool_pass += 1

        if actual_approval_required == item["expected_approval_required"]:
            approval_pass += 1

        print("=" * 80)
        print("ID:", item["id"])
        print("Purpose:", item["purpose"])
        print("Input:", item["user_input"])
        print("Expected intent:", item["expected_intent"])
        print("Actual intent:", actual_intent)
        print("Expected tool:", item["expected_tool"])
        print("Actual tool:", actual_tool)
        print("Expected approval:", item["expected_approval_required"])
        print("Actual approval:", actual_approval_required)
        print("Router reason:", result.get("router_reason"))
        print("Router confidence:", result.get("router_confidence"))
        print("Steps:", result.get("steps"))

    print("\nAgent Eval Result")
    print("Total:", total)

    if total == 0:
        print("No eval cases found.")
        return

    print("Intent Pass Rate:", intent_pass / total)
    print("Tool Pass Rate:", tool_pass / total)
    print("Approval Pass Rate:", approval_pass / total)


if __name__ == "__main__":
    main()

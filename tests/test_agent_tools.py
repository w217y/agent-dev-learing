from app.agent.tools import (
    create_ticket_draft_tool,
    draft_email_tool,
)


def test_create_ticket_draft_tool():
    result = create_ticket_draft_tool(
        title="报销资料缺失",
        description="用户报销资料缺失，需要补充材料。",
        priority="medium",
    )

    assert result["type"] == "ticket"
    assert result["title"] == "报销资料缺失"
    assert result["description"] == "用户报销资料缺失，需要补充材料。"
    assert result["priority"] == "medium"
    assert result["status"] == "draft"
    assert "draft_id" in result
    assert "created_at" in result


def test_draft_email_tool():
    result = draft_email_tool(
        to="finance@example.com",
        subject="报销资料补充说明",
        body="报销资料已经补齐，请协助审核。",
    )

    assert result["type"] == "email"
    assert result["to"] == "finance@example.com"
    assert result["subject"] == "报销资料补充说明"
    assert result["body"] == "报销资料已经补齐，请协助审核。"
    assert result["status"] == "draft"
    assert "draft_id" in result

def test_sql_query_tool_rejects_unknown_query():
    from app.agent.tools import sql_query_tool

    result = sql_query_tool("drop_all_tables")

    assert "error" in result
    assert "不支持" in result["error"]

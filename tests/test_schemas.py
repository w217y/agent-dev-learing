import pytest

from pydantic import ValidationError
from app.schemas import ChatMessage, ChatRequest

def test_chat_message_valid():
    msg = ChatMessage(role="user", content="Hello")
    assert msg.role == "user"

def test_chat_message_invalid_role():
    with pytest.raises(ValidationError):
        ChatMessage(role="bad_role", content="Hello")


def test_chat_request_valid():
    req = ChatRequest(
        messages=[ChatMessage(role="user", content="Hello")],
        temperature=0.2,
    )
    assert len(req.messages) == 1
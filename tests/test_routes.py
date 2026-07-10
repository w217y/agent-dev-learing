from app.main import app

def test_expected_routes_registered():
    paths = set(app.openapi()["paths"].keys())

    assert "/health" in paths
    assert "/api/chat" in paths
    assert "/api/chat/stream" in paths
    assert "/api/extract-task" in paths
    assert "/api/tool-chat" in paths 
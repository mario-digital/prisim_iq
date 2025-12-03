from fastapi.testclient import TestClient

from src.main import create_app


def client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_chat_health_endpoint() -> None:
    with client() as c:
        r = c.get("/api/v1/chat/health")
        assert r.status_code == 200
        data = r.json()
        assert data.get("status") == "ok"
        assert "model" in data
        assert isinstance(data.get("tools_count"), int)
        assert "time" in data


def test_chat_tools_endpoint() -> None:
    with client() as c:
        r = c.get("/api/v1/chat/tools")
        assert r.status_code == 200
        tools = r.json()
        assert isinstance(tools, list)
        assert any(t.get("name") == "optimize_price" for t in tools)

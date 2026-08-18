import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200


def test_notify_missing_order_id(client):
    resp = client.post("/notify", json={"channel": "email"})
    assert resp.status_code == 400


def test_notify_success(client):
    resp = client.post(
        "/notify",
        json={"order_id": "order-123", "channel": "email", "message": "Order confirmed"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "sent"
    assert data["order_id"] == "order-123"


def test_list_notifications(client):
    client.post("/notify", json={"order_id": "order-999"})
    resp = client.get("/notifications")
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(n["order_id"] == "order-999" for n in data["notifications"])

import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Restore the in-memory activities to their original state after each test."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


# ---------------------------------------------------------------------------
# GET /activities
# ---------------------------------------------------------------------------

def test_get_activities_returns_all():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == len(activities)


def test_get_activities_shape():
    response = client.get("/activities")
    for activity in response.json().values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# ---------------------------------------------------------------------------
# POST /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_signup_success():
    response = client.post(
        "/activities/Soccer Team/signup",
        params={"email": "new@mergington.edu"},
    )
    assert response.status_code == 200
    assert "new@mergington.edu" in response.json()["message"]
    assert "new@mergington.edu" in activities["Soccer Team"]["participants"]


def test_signup_unknown_activity():
    response = client.post(
        "/activities/Underwater Basket Weaving/signup",
        params={"email": "new@mergington.edu"},
    )
    assert response.status_code == 404


def test_signup_duplicate_participant():
    # michael is already in Chess Club
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )
    assert response.status_code == 400


# ---------------------------------------------------------------------------
# DELETE /activities/{activity_name}/signup
# ---------------------------------------------------------------------------

def test_unregister_success():
    response = client.delete(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"},
    )
    assert response.status_code == 200
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_unknown_activity():
    response = client.delete(
        "/activities/Underwater Basket Weaving/signup",
        params={"email": "michael@mergington.edu"},
    )
    assert response.status_code == 404


def test_unregister_participant_not_signed_up():
    response = client.delete(
        "/activities/Soccer Team/signup",
        params={"email": "nobody@mergington.edu"},
    )
    assert response.status_code == 404

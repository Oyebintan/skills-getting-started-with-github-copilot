import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

initial = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(initial))
    yield


client = TestClient(app)


def test_get_activities():
    # Arrange (fixture resets state)
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    assert "Chess Club" in resp.json()


def test_signup_success():
    # Arrange
    activity = "Chess Club"
    email = "test.user@example.com"
    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert resp.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]


def test_signup_duplicate():
    # Arrange
    activity = "Chess Club"
    email = "dup@example.com"
    client.post(f"/activities/{activity}/signup", params={"email": email})
    # Act
    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    # Assert
    assert resp.status_code == 400


def test_remove_participant_success():
    # Arrange
    activity = "Chess Club"
    before = client.get("/activities").json()[activity]["participants"]
    assert before
    email = before[0]
    # Act
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    # Assert
    assert resp.status_code == 200
    assert resp.json().get("remaining_participants") == len(before) - 1


def test_remove_participant_not_found():
    # Arrange
    activity = "Chess Club"
    email = "not@present.example"
    # Act
    resp = client.delete(f"/activities/{activity}/participants", params={"email": email})
    # Assert
    assert resp.status_code == 404

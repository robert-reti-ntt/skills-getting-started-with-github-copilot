import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data

def test_signup_success():
    response = client.post("/activities/Soccer Team/signup?email=tester@mergington.edu")
    assert response.status_code == 200
    assert "Signed up tester@mergington.edu for Soccer Team" in response.json()["message"]

    # Clean up for idempotency
    data = client.get("/activities").json()
    data["Soccer Team"]["participants"].remove("tester@mergington.edu")

def test_signup_duplicate():
    # Add once
    client.post("/activities/Drama Club/signup?email=drama@mergington.edu")
    # Try duplicate
    response = client.post("/activities/Drama Club/signup?email=drama@mergington.edu")
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]
    # Clean up
    data = client.get("/activities").json()
    data["Drama Club"]["participants"].remove("drama@mergington.edu")

def test_signup_activity_not_found():
    response = client.post("/activities/Nonexistent/signup?email=ghost@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_signup_activity_full():
    # Fill up Math Olympiad
    for i in range(10):
        client.post(f"/activities/Math Olympiad/signup?email=math{i}@mergington.edu")
    response = client.post("/activities/Math Olympiad/signup?email=overflow@mergington.edu")
    assert response.status_code == 400
    assert "Activity is full" in response.json()["detail"]
    # Clean up
    data = client.get("/activities").json()
    data["Math Olympiad"]["participants"] = []

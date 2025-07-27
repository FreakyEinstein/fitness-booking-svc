"""
Test Cases:
1. Instructor signup via /auth/signup
2. Instructor login via /auth/login
3. Create a class via /classes
4. Get all users who booked the instructor's class via /book/bookings/me
5. Try to get bookings for a class not owned by instructor (should fail)
"""

import pytest
from fastapi.testclient import TestClient
from app import app
import subprocess

client = TestClient(app)


@pytest.fixture(scope="module")
def instructor_token():
    # 1. Signup as instructor
    signup_resp = client.post(
        "/auth/signup",
        data={
            "name": "Test Instructor",
            "email": "testinstructor@example.com",
            "password": "testpassword",
            "client_id": "instructor"
        }
    )
    assert signup_resp.status_code in (200, 403)

    # 2. Login as instructor
    login_resp = client.post(
        "/auth/login",
        data={
            "username": "testinstructor@example.com",
            "password": "testpassword",
            "client_id": "instructor"
        }
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return token


def test_instructor_can_create_class_and_view_bookings(instructor_token):
    # 3. Create a class
    import datetime
    from pytz import timezone as pytz_timezone
    ist = pytz_timezone("Asia/Kolkata")
    dt = datetime.datetime.now(ist) + datetime.timedelta(days=1)
    dt_str = dt.strftime("%Y-%m-%dT%H:%M:%S")
    create_resp = client.post(
        "/classes",
        json={
            "name": "Instructor Test Class",
            "datetime_of_class": dt_str,
            "total_slots": 5,
            "duration_in_hours": 1
        },
        headers={"Authorization": f"Bearer {instructor_token}"}
    )
    assert create_resp.status_code == 200
    assert create_resp.json()["success"]

    # 4. Get all classes to find the created class id
    resp = client.get(
        "/classes", headers={"Authorization": f"Bearer {instructor_token}"})
    assert resp.status_code == 200
    classes = resp.json()
    created_class = next(
        (c for c in classes if c["name"] == "Instructor Test Class"), None)
    assert created_class is not None
    class_id = created_class["id"]

    # 5. Check all users who booked this class (should be empty initially)
    bookings_resp = client.get(
        f"/book/bookings/me?class_id={class_id}",
        headers={"Authorization": f"Bearer {instructor_token}"}
    )
    assert bookings_resp.status_code == 200
    users = bookings_resp.json()
    assert isinstance(users, list)
    assert len(users) == 0


def test_instructor_cannot_view_other_instructor_class_bookings(instructor_token):
    # Try to get bookings for a class not owned by this instructor
    # Use a class id that is not created by "testinstructor@example.com"
    resp = client.get(
        "/classes", headers={"Authorization": f"Bearer {instructor_token}"})
    assert resp.status_code == 200
    classes = resp.json()
    other_class = next((c for c in classes if c.get("instructor_email")
                       and c["instructor_email"] != "testinstructor@example.com"), None)
    if other_class:
        class_id = other_class["id"]
        bookings_resp = client.get(
            f"/book/bookings/me?class_id={class_id}",
            headers={"Authorization": f"Bearer {instructor_token}"}
        )
        assert bookings_resp.status_code == 403


def teardown_module(module):
    # Cleanup test records after all tests in this module
    subprocess.run(["python3", "scripts/cleanup_test_data.py"])

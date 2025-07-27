"""
Test Cases:
1. User signup via /auth/signup
2. User login via /auth/login
3. Get all classes via /classes
4. Book a class via /book
5. Get all user bookings via /book/bookings/me
6. Book another class and check bookings again
"""

import pytest
from fastapi.testclient import TestClient
from app import app
import subprocess

client = TestClient(app)


@pytest.fixture(scope="module")
def user_token():
    # 1. Signup as user
    signup_resp = client.post(
        "/auth/signup",
        data={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "testpassword",
            "client_id": "user"
        }
    )
    # Accept 200 or 403 (already exists)
    assert signup_resp.status_code in (200, 403)

    # 2. Login as user
    login_resp = client.post(
        "/auth/login",
        data={
            "username": "testuser@example.com",
            "password": "testpassword",
            "client_id": "user"
        }
    )
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    return token


def test_user_can_book_and_view_bookings(user_token):
    # 3. Get list of all classes
    resp = client.get(
        "/classes", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200
    classes = resp.json()
    assert isinstance(classes, list)
    assert len(classes) > 1
    class_id_1 = classes[0]["id"]
    class_id_2 = classes[1]["id"]

    # 4. Book first class
    book_resp = client.post(
        "/book",
        json={"class_id": class_id_1},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert book_resp.status_code == 200
    assert book_resp.json()["success"]

    # 5. Check all bookings (should include class_id_1)
    bookings_resp = client.get(
        "/book/bookings/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert bookings_resp.status_code == 200
    bookings = bookings_resp.json()
    assert any(b["class_id"] == class_id_1 for b in bookings)

    # 6. Book another class
    book_resp2 = client.post(
        "/book",
        json={"class_id": class_id_2},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert book_resp2.status_code == 200
    assert book_resp2.json()["success"]

    # 7. Check all bookings (should include both class_id_1 and class_id_2)
    bookings_resp2 = client.get(
        "/book/bookings/me",
        headers={"Authorization": f"Bearer {user_token}"}
    )
    assert bookings_resp2.status_code == 200
    bookings2 = bookings_resp2.json()
    booked_classes = [b["class_id"] for b in bookings2]
    assert class_id_1 in booked_classes
    assert class_id_2 in booked_classes


def test_user_cannot_book_same_class_twice(user_token):
    # Get list of all classes
    resp = client.get(
        "/classes", headers={"Authorization": f"Bearer {user_token}"})
    assert resp.status_code == 200
    classes = resp.json()
    class_id = classes[0]["id"]

    # Try booking the same class again
    book_resp = client.post(
        "/book",
        json={"class_id": class_id},
        headers={"Authorization": f"Bearer {user_token}"}
    )
    # Should fail with 403
    assert book_resp.status_code == 403


def teardown_module(module):
    # Cleanup test records after all tests in this module
    subprocess.run(["python3", "scripts/cleanup_test_data.py"])

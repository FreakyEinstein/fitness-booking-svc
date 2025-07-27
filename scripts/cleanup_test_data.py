import os
import json

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
storage_dir = os.path.join(BASE, "app", "storage")

# Identifiers for test data
TEST_EMAILS = {
    "testuser@example.com",
    "testinstructor@example.com",
    "Test User",
    "Test Instructor"
}
TEST_CLASS_NAMES = {
    "Instructor Test Class"
}


def filter_users(data):
    return [u for u in data if u.get("email") not in TEST_EMAILS and u.get("name") not in TEST_EMAILS]


def filter_classes(data):
    return [c for c in data if c.get("name") not in TEST_CLASS_NAMES]


def filter_bookings(data):
    return [b for b in data if b.get("user_email") not in TEST_EMAILS and b.get("user_name") not in TEST_EMAILS]


def clean_file(filename, filter_func):
    path = os.path.join(storage_dir, filename)
    if not os.path.exists(path):
        return
    with open(path, "r") as f:
        try:
            data = json.load(f)
        except Exception:
            data = []
    cleaned = filter_func(data)
    with open(path, "w") as f:
        json.dump(cleaned, f, indent=4)


if __name__ == "__main__":
    clean_file("users.json", filter_users)
    clean_file("classes.json", filter_classes)
    clean_file("bookings.json", filter_bookings)
    print("Test records created by test_ scripts have been cleaned up.")

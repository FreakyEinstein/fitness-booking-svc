# Fitness Class Booking API

A backend system built with **FastAPI** that powers a fitness class booking application. It supports two main user roles:

- **Users**: Can view and book classes
- **Instructors**: Can create classes and view who booked them

This REST API handles authentication, role-based access, class scheduling, and booking logic with conflict prevention.

## Project Setup

Follow these steps to set up the project after cloning it for the first time:

### 1. Install Pipenv

If you don't have Pipenv installed already:

```bash
pip install pipenv
```

### 2. Install Project Dependencies

```bash
pipenv install
```

This will install all dependencies listed in the `Pipfile`.

### 3. Configure Environment Variables (Optional)

Create a `.env` file in the project root directory to customize the application settings. All environment variables are optional and have default values if not specified:

```env
JWT_SECRET_KEY=7e98823e91c2ba8e13ada1564c8f13654221f323
JWT_ALGORITHM=HS256
JWT_EXPIRY_IN_HOURS=6
APP_TIMEZONE="Asia/Kolkata"
```

### 4. Activate the Virtual Environment

```bash
pipenv shell
```

This activates your environment where you can run the app or tests.

## Running the Server

### Production Mode

```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Development Mode (with auto-reload)

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### Accessing API Documentation

After starting the server, you can access the interactive API documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Running Tests

### Run All Tests

```bash
PYTHONPATH=$PYTHONPATH:../app pytest
```

### Clean Up Test Data

```bash
PYTHONPATH=$PYTHONPATH:../app python scripts/cleanup_test_data.py
```

**Important**: Always run the cleanup script before running tests. Tests create sample data, and without cleanup, duplicate key errors may occur.

## API Workflows

### User Workflow

1. **Signup** via `POST /auth/signup`
2. **Login** via `POST /auth/login`
3. **View All Classes** via `GET /classes`
4. **Book a Class** via `POST /book`
5. **View My Bookings** via `GET /book/bookings/me`
6. **Book Another Class** and verify bookings again

### Instructor Workflow

1. **Signup** via `POST /auth/signup`
2. **Login** via `POST /auth/login`
3. **Create a Class** via `POST /classes`
4. **View All Bookings for Instructor's Classes** via `GET /book/bookings/me`
5. **Attempt to View Bookings for Others' Classes** → should fail (unauthorized access)

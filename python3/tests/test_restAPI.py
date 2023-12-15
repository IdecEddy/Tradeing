from fastapi.testclient import TestClient
from src.restapi import Sqlite_db, app, SECRET_KEY, ALGORITHM
import jwt


# Mocking the database for testing purposes
class MockSqliteDatabase(Sqlite_db):
    def __init__(self):
        pass

    def database_select_user_by_username(self, username):
        # Customize the mock database response based on your test cases
        if username == "existing_user":
            return (1, "existing_user", "hashed_password")
        else:
            return None


client = TestClient(app)


def test_protected_route_with_valid_token():
    # Generate a valid token for testing
    valid_token = jwt.encode({"sub": "testuser"}, SECRET_KEY, algorithm=ALGORITHM)

    # Make a request with the valid token
    response = client.get("/protected-route", cookies={"access_token": valid_token})

    # Assert that the response status code is 200
    assert response.status_code == 200

    # Assert that the response contains the expected message and user information
    assert response.json() == {"message": "This is a protected route", "user": {"sub": "testuser"}}


def test_protected_route_with_invalid_token():
    # Make a request with an invalid token
    response = client.get("/protected-route", cookies={"access_token": "invalid_token"})

    # Assert that the response status code is 401
    assert response.status_code == 401

    # Assert that the response contains the expected error message
    assert response.json() == {"detail": "Could not validate credentials"}

    
def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == "Hello World"


def test_login_successful(monkeypatch):
    # Override the default database with the mock database
    monkeypatch.setattr(
            Sqlite_db,
            'database_select_user_by_username',
            lambda x, y: (1, "existing_user", "hashed_password"))

    # Send a POST request to the login endpoint with valid credentials
    response = client.post(
        "/login",
        data={"username": "existing_user", "password": "hashed_password"},
    )

    # Assert the response
    assert response.status_code == 200
    assert "access_token" in response.cookies

    # Reset dependency overrides to avoid affecting other tests
    app.dependency_overrides = {}


def test_login_invalid_username(monkeypatch):
    # Override the default database with the mock database
    monkeypatch.setattr(
            Sqlite_db,
            'database_select_user_by_username',
            lambda x, y: (1, "existing_user", "hashed_password"))

    # Send a POST request to the login endpoint with valid credentials
    response = client.post(
        "/login",
        data={"username": "bad_user", "password": "hashed_password"},
    )

    # Assert the response
    assert response.status_code == 401
    assert "access_token" not in response.cookies

    # Reset dependency overrides to avoid affecting other tests
    app.dependency_overrides = {}


def test_login_invalid_password(monkeypatch):
    # Override the default database with the mock database
    monkeypatch.setattr(
            Sqlite_db,
            'database_select_user_by_username',
            lambda x, y: (1, "existing_user", "hashed_password"))

    # Send a POST request to the login endpoint with valid credentials
    response = client.post(
        "/login",
        data={"username": "existing_user", "password": "bad_password"},
    )

    # Assert the response
    assert response.status_code == 401
    assert "access_token" not in response.cookies

    # Reset dependency overrides to avoid affecting other tests
    app.dependency_overrides = {}


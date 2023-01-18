import pytest
from fastapi.testclient import TestClient

from .setup import (
    db,
    client,
    user,
    token,
    authenticated_client,
)


@pytest.mark.parametrize("email, password, status_code", [
    (None, "password123", 422),
    ("example@example.com", None, 422),
    (None, None, 422),
    ("", "", 422),
    ("", "password123", 422),
    ("example@example.com", "", 422),
    ("example@example.com", "password123", 201)
])
def test_signup(client, email, password, status_code):
    signup_data = {
        "email": email,
        "password": password
    }

    response = client.post("/users/", json=signup_data)
    
    assert response.status_code == status_code


@pytest.mark.parametrize("id, status_code", [
    (1, 200),
    (2, 403),
    (100000, 403),
    ("qwe", 422),
    ("", 405)
])
def test_get_user_by_id(authenticated_client, id, status_code):
    response = authenticated_client.get(f"/users/{id}")

    assert response.status_code == status_code

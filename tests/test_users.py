import pytest
from fastapi.testclient import TestClient

from .setup import (
    db,
    client,
    user_1,
    authenticated_client_1,
    user_2,
    authenticated_client_2
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
def test_signup(client: TestClient, email: str, password: str, status_code: int):
    signup_data = {
        "email": email,
        "password": password
    }

    response = client.post("/users/", json=signup_data)
    
    assert response.status_code == status_code

import os

from dotenv import load_dotenv
from jose import jwt, JWTError
import pytest

from .setup import (
    db,
    client,
    user,
    token,
    authenticated_client,
)
from api.oauth2 import decrypt_token

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

JWT_HASHING_ALGORITHM = os.getenv("JWT_HASHING_ALGORITHM")


def test_login_success(client, user):
    login_data = {
        "username": user["email"],
        "password": user["password"]
    }

    response = client.post("/login", data=login_data)

    assert response.status_code == 200

    token = response.json().get("access_token")

    assert token is not None

    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_HASHING_ALGORITHM])

    user_id = payload.get("user_id")

    assert user_id == user["id"]


def test_login_fail(client, user):
    login_data = {
        "username": user["email"],
        "password": "aaaaaaaaaaaaaaaaaa"
    }

    response = client.post("/login", data=login_data)
    assert response.status_code == 403

    login_data["username"] = "aaaaaaaa"
    response = client.post("/login", data=login_data)
    assert response.status_code == 403

    login_data["password"] = "password1"
    response = client.post("/login", data=login_data)
    assert response.status_code == 403

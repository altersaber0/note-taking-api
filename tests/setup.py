import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from ..api.main import app
from ..api.database.db_setup import get_db, Base

SQLITE_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLITE_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db() -> Session:

    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db: Session) -> TestClient:

    def override_get_db() -> Session:
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)


@pytest.fixture
def user_1(client: TestClient) -> dict:
    signup_data = {
        "email": "example1@example.com",
        "password": "password1"
    }

    response = client.post("/users/", json=signup_data)
    
    assert response.status_code == 201

    user = response.json()

    assert user["id"] == 1

    user["password"] = signup_data["password"]

    return user


@pytest.fixture
def authenticated_client_1(client: TestClient, user_1: dict) -> TestClient:
    login_data = {
        "username": user_1["email"],
        "password": user_1["password"]
    }

    response = client.post("/login", data=login_data)

    assert response.status_code == 200

    token = response.json().get("access_token")

    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    return client


@pytest.fixture
def user_2(client: TestClient) -> dict:
    signup_data = {
        "email": "example2@example.com",
        "password": "password2"
    }

    response = client.post("/users/", json=signup_data)
    
    assert response.status_code == 201

    user = response.json()

    assert user["id"] == 2

    user["password"] = signup_data["password"]

    return user


@pytest.fixture
def authenticated_client_2(client: TestClient, user_2: dict) -> TestClient:
    login_data = {
        "username": user_2["email"],
        "password": user_2["password"]
    }

    response = client.post("/login", data=login_data)

    assert response.status_code == 200

    token = response.json().get("access_token")

    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    return client

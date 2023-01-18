import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from api.main import app
from api.database.db_setup import get_db, Base
from api.oauth2 import create_token

SQLITE_DATABASE_URL = "sqlite:///./tests/test.db"

engine = create_engine(
    SQLITE_DATABASE_URL, connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db() -> Session:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db: Session) -> TestClient:

    def override_get_db() -> Session:
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest.fixture
def user(client: TestClient) -> dict:
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
def token(user: dict) -> str:
    return create_token(user["id"])


@pytest.fixture
def authenticated_client(token: str, client: TestClient) -> TestClient:

    client.headers.update({"Authorization": f"Bearer {token}"})

    return client

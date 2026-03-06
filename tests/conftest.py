import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.main import app
from app.database import Base
from app.dependencies import get_db
from app import crud


TEST_DATABASE_URL = "sqlite:///./test_shortener.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


class FakeRedis:
    def __init__(self):
        self.storage = {}

    def get(self, key):
        return self.storage.get(key)

    def set(self, key, value):
        self.storage[key] = value

    def delete(self, key):
        self.storage.pop(key, None)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    if os.path.exists("test_shortener.db"):
        os.remove("test_shortener.db")

    Base.metadata.create_all(bind=engine)

    yield

    Base.metadata.drop_all(bind=engine)

    if os.path.exists("test_shortener.db"):
        os.remove("test_shortener.db")


@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db_session, monkeypatch):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    fake_redis = FakeRedis()
    monkeypatch.setattr(crud, "redis_client", fake_redis)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    register_payload = {
        "username": "polina",
        "email": "polina@test.com",
        "password": "123456"
    }

    client.post("/register", json=register_payload)

    response = client.post(
        "/login",
        data={"username": "polina", "password": "123456"}
    )

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}
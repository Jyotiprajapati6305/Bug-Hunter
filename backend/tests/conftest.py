"""Pytest fixtures: an isolated SQLite test database per test, wired into the
FastAPI app via dependency override, plus a TestClient and seeded roles."""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key")
os.environ.setdefault("CELERY_BROKER_URL", "memory://")
os.environ.setdefault("CELERY_RESULT_BACKEND", "cache+memory://")
os.environ.setdefault("ENVIRONMENT", "test")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.deps import get_db_session
from app.db.base import Base
from app.main import app
from app.models.user import Role

TEST_DATABASE_URL = "sqlite://"  # in-memory, shared via StaticPool


@pytest.fixture()
def db_engine():
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    # seed roles required by registration/role-guards
    for role_name in ("admin", "developer", "tester"):
        session.add(Role(name=role_name, description=role_name))
    session.commit()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db_session] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def register_and_login(client):
    """Helper: registers a user with the given role and returns (tokens, headers)."""

    def _do(email: str, username: str, password: str, role: str = "tester"):
        resp = client.post(
            "/api/v1/auth/register",
            json={"email": email, "username": username, "password": password, "role": role},
        )
        assert resp.status_code == 201, resp.text
        login_resp = client.post("/api/v1/auth/login", json={"email": email, "password": password})
        assert login_resp.status_code == 200, login_resp.text
        tokens = login_resp.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        return tokens, headers

    return _do

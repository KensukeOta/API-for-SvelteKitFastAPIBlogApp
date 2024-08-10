import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine, select
from sqlmodel.pool import StaticPool

from ..main import app
from ..database import get_session
from ..models.user_model import User


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def test_create_oauth_user(client: TestClient):
    response = client.post(
        "/v1/oauth", 
        json={"name": "hoge", "email": "hoge@example.com", "image": "hoge.png", "provider": "credentials"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "hoge"
    assert data["email"] == "hoge@example.com"
    assert data["image"] == "hoge.png"
    assert data["provider"] == "credentials"


def test_create_oauth_user_with_existing_user(session: Session, client: TestClient):
    existing_user = User(name="hoge", email="hoge@example.com", image="hoge.png", provider="credentials", password_digest="asfasfsafsafsasfasfff")
    session.add(existing_user)
    session.commit()

    response = client.post(
        "/v1/oauth", 
        json={"name": "hoge", "email": "hoge@example.com", "image": "hoge.png", "provider": "credentials", "password": "hogehoge", "password_confirmation": "hogehoge"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == existing_user.name
    assert data["email"] == existing_user.email
    assert data["image"] == existing_user.image
    assert data["provider"] == existing_user.provider
    
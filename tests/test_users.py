import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
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


def test_create_user(client: TestClient):
    response = client.post(
        "/v1/users", 
        json={"name": "hoge", "email": "hoge@example.com", "image": "hoge.png", "provider": "credentials", "password": "hogehoge", "password_confirmation": "hogehoge"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "hoge"
    assert data["email"] == "hoge@example.com"
    assert data["image"] == "hoge.png"
    assert data["provider"] == "credentials"


def test_create_user_invalid(session: Session, client: TestClient):
    user = User(name="hoge", email="hoge@example.com", image="hoge.png", provider="credentials", password_digest="asfasfsafsafsasfasfff")
    session.add(user)
    session.commit()

    response = client.post(
        "/v1/users", 
        json={"name": "hoge", "email": "hoge@example.com", "image": "hoge.png", "provider": "credentials", "password": "hogehoge", "password_confirmation": "hogehoge"}
    )

    assert response.status_code == 409

    
def test_read_users(session: Session, client: TestClient):
    user_1 = User(name="hoge", email="hoge@example.com", image="hoge.png", provider="credentials", password_digest="asfasfsafsafsasfasfff")
    user_2 = User(name="fuga", email="fuga@example.com", image="fuga.png", provider="google", password_digest="afafgasdfsafsdffaf")
    session.add(user_1)
    session.add(user_2)
    session.commit()

    response = client.get("/v1/users")
    data = response.json()

    assert response.status_code == 200

    assert len(data) == 2
    assert data[0]["name"] == user_1.name
    assert data[0]["email"] == user_1.email
    assert data[0]["image"] == user_1.image
    assert data[0]["provider"] == user_1.provider
    assert data[1]["name"] == user_2.name
    assert data[1]["email"] == user_2.email
    assert data[1]["image"] == user_2.image
    assert data[1]["provider"] == user_2.provider

  
def test_read_users_with_query_params_email_and_provider(session: Session, client: TestClient):
    user = User(name="hoge", email="hoge@example.com", image="hoge.png", provider="credentials", password_digest="asfasfsafsafsasfasfff")
    session.add(user)
    session.commit()

    response = client.get(f"/v1/users?email={user.email}&provider={user.provider}")
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == user.name
    assert data["email"] == user.email
    assert data["image"] == user.image
    assert data["provider"] == user.provider

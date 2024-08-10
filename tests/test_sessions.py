import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from passlib.context import CryptContext

from ..main import app
from ..database import get_session
from ..models.user_model import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ユーザーが入力したパスワードをハッシュ化したバスワードにする
def get_password_hash(password):
    return pwd_context.hash(password)


# ユーザーが入力したパスワードとハッシュ化したパスワードが一致するか確認する
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


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


def test_authenticate(session: Session, client: TestClient):
    user = User(name="hoge", email="hoge@example.com", image="hoge.png", provider="credentials", password_digest=get_password_hash("hogehoge"))
    session.add(user)
    session.commit()

    response = client.post(
        "/v1/sessions", 
        json={"email": "hoge@example.com", "password": "hogehoge", "provider": "credentials"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "hoge"
    assert data["email"] == "hoge@example.com"
    assert data["image"] == "hoge.png"
    assert data["provider"] == "credentials"


def test_authenticate_invalid_user(session: Session, client: TestClient):
    user = User(name="hoge", email="hoge@example.com", image="hoge.png", provider="credentials", password_digest=get_password_hash("hogehoge"))
    session.add(user)
    session.commit()

    response = client.post(
        "/v1/sessions", 
        json={"email": "fuga@example.com", "password": "hogehoge", "provider": "credentials"}
    )

    assert response.status_code == 401


def test_authenticate_invalid_password(session: Session, client: TestClient):
    user = User(name="hoge", email="hoge@example.com", image="hoge.png", provider="credentials", password_digest=get_password_hash("hogehoge"))
    session.add(user)
    session.commit()

    response = client.post(
        "/v1/sessions",
        json={"email": "fuga@example.com", "password": "fugafuga", "provider": "credentials"}
    )

    assert response.status_code == 401
    
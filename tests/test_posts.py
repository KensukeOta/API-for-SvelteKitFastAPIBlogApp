import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from ..main import app
from ..database import get_session
from ..models.post_model import Post


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


def test_create_post(client: TestClient):
    response = client.post(
        "/v1/posts", 
        json={"title": "Sample Title", "body": "Sample Body", "user_id": 1}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == "Sample Title"
    assert data["body"] == "Sample Body"
    assert data["user_id"] == 1


def test_create_post_incomplete(client: TestClient):
    # No user_id
    response = client.post(
        "/v1/posts", 
        json={"title": "Hoge", "body": "Fuga"}
    )
    assert response.status_code == 422


def test_create_post_invalid(client: TestClient):
    # secret_name has an invalid type
    response = client.post(
        "/v1/posts",
        json={
            "title": "Deadpond",
            "body": {"message": "Do you wanna know my secret identity?"},
            "user_id": 1,
        },
    )
    assert response.status_code == 422


def test_read_posts(session: Session, client: TestClient):
    post_1 = Post(title="Hello", body="Hello World", user_id=1)
    post_2 = Post(title="Sample Title", body="Sample Body", user_id=2)
    session.add(post_1)
    session.add(post_2)
    session.commit()

    response = client.get("/v1/posts")
    data = response.json()

    assert response.status_code == 200

    assert len(data) == 2
    assert data[0]["title"] == post_2.title
    assert data[0]["body"] == post_2.body
    assert data[0]["user_id"] == post_2.user_id
    assert data[1]["title"] == post_1.title
    assert data[1]["body"] == post_1.body
    assert data[1]["user_id"] == post_1.user_id
    

def test_read_post(session: Session, client: TestClient):
    post = Post(title="Hoge", body="HogeHoge", user_id=1)
    session.add(post)
    session.commit()

    response = client.get(f"/v1/posts/{post.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == post.title
    assert data["body"] == post.body
    assert data["user_id"] == post.user_id


def test_read_post_not_found(session: Session, client: TestClient):
    post = Post(title="Hoge", body="HogeHoge", user_id=1)
    session.add(post)
    session.commit()

    response = client.get("/v1/posts/100")

    assert response.status_code == 404


def test_update_post(session: Session, client: TestClient):
    post = Post(title="Sample Title", body="Sample Post", user_id=1)
    session.add(post)
    session.commit()

    response = client.patch(
        f"/v1/posts/{post.id}", 
        json={"title": "Sample Title Update"}
    )
    data = response.json()

    assert response.status_code == 200
    assert data["title"] == "Sample Title Update"
    assert data["body"] == "Sample Post"
    assert data["user_id"] == post.user_id

    
def test_update_post_not_found(session: Session, client: TestClient):
    post = Post(title="Sample Title", body="Sample Post", user_id=1)
    session.add(post)
    session.commit()

    response = client.patch(
        "/v1/posts/100", 
        json={"title": "Sample Title Update"}
    )

    assert response.status_code == 404


def test_delete_post(session: Session, client: TestClient):
    post = Post(title="Sample Title", body="Sample Body", user_id=1)
    session.add(post)
    session.commit()

    response = client.delete(f"/v1/posts/{post.id}")

    post_in_db = session.get(Post, post.id)

    assert response.status_code == 200

    assert post_in_db is None


def test_delete_post_not_found(session: Session, client: TestClient):
    post = Post(title="Sample Title", body="Sample Body", user_id=1)
    session.add(post)
    session.commit()

    response = client.delete("/v1/posts/100")

    assert response.status_code == 404

from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import desc, select, Session

from ..database import get_session
from ..models.post_model import Post, PostCreate, PostUpdate, PostPublic
from ..models.responses import PostPublicWithUser

router = APIRouter(
    prefix="/v1",
    tags=["posts"],
)


@router.post("/posts")
def create_post(*, session: Annotated[Session, Depends(get_session)], post: PostCreate) -> PostPublic:
    db_post = Post.model_validate(post)
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@router.get("/posts")
def read_posts(*, session: Annotated[Session, Depends(get_session)]) -> list[PostPublicWithUser]:
    posts = session.exec(select(Post).order_by(desc(Post.created_at))).all()
    return posts


@router.get("/posts/{id}")
def read_post(*, session: Session = Depends(get_session), id: int) -> PostPublicWithUser:
    post = session.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@router.patch("/posts/{id}")
def update_post(*, session: Session = Depends(get_session), id: int, post: PostUpdate) -> PostPublic:
    db_post = session.get(Post, id)
    if not db_post:
        raise HTTPException(status_code=404, detail="Post not found")
    post_data = post.model_dump(exclude_unset=True)
    db_post.sqlmodel_update(post_data)
    db_post.updated_at = datetime.now()
    session.add(db_post)
    session.commit()
    session.refresh(db_post)
    return db_post


@router.delete("/posts/{id}")
def delete_post(*, session: Session = Depends(get_session), id: int):
    post = session.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    session.delete(post)
    session.commit()
    return {"ok": True}

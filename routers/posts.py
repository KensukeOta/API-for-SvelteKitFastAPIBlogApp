from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import select, Session

from ..database import get_session
from ..models.post_model import Post, PostCreate, PostPublic
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

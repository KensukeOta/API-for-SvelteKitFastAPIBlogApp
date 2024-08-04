from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
from sqlmodel import select, Session

from ..database import get_session
from ..models.user_model import User, UserCreate, UserPublic
from ..models.responses import UserPublicWithPosts

router = APIRouter(
    prefix="/v1",
    tags=["users"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ユーザーが入力したパスワードをハッシュ化したバスワードにする
def get_password_hash(password):
    return pwd_context.hash(password)


@router.post("/users")
def create_user(*, session: Annotated[Session, Depends(get_session)], user: UserCreate) -> UserPublic:
    is_existing_user = session.exec(select(User).where(User.email == user.email, User.provider == user.provider)).first()
    if is_existing_user:
        raise HTTPException(status_code=409, detail="ユーザーは既に存在します")
    
    password_digest = get_password_hash(user.password)
    extra_data = {"password_digest": password_digest}
    db_user = User.model_validate(user, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
    

@router.get("/users")
def read_users(*, email: str | None = None, provider: str | None = None, session: Annotated[Session, Depends(get_session)]) -> list[UserPublicWithPosts] | UserPublic:
    if email and provider:
        user = session.exec(select(User).where(User.email == email, User.provider == provider)).one()
        return user
    users = session.exec(select(User)).all()
    return users
    
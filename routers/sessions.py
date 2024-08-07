from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlmodel import select, Session

from ..database import get_session
from ..models.user_model import User, UserAuth, UserPublic

router = APIRouter(
    prefix="/v1",
    tags=["sessions"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ユーザーが入力したパスワードとハッシュ化したパスワードが一致するか確認する
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@router.post("/sessions")
def authenticate(*, session: Annotated[Session, Depends(get_session)], user: UserAuth) -> UserPublic:
    is_existing_user = session.exec(select(User).where(User.email == user.email, User.provider == user.provider)).first()

    if is_existing_user and verify_password(user.password, is_existing_user.password_digest):
        return is_existing_user
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="ログインに失敗しました")


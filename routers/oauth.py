import random
import string

from typing import Annotated

from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from sqlmodel import select, Session

from ..database import get_session
from ..models.user_model import User, UserPublic, OAuthUserCreate

router = APIRouter(
    prefix="/v1",
    tags=["oauth"],
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_random_password(length: int = 12) -> str:
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))


# ユーザーが入力したパスワードをハッシュ化したバスワードにする
def get_password_hash(password):
    return pwd_context.hash(password)


@router.post("/oauth")
def create_oauth_user(*, session: Annotated[Session, Depends(get_session)], user: OAuthUserCreate) -> UserPublic:
    # ユーザーが既に存在しているかチェック
    is_existing_user = session.exec(select(User).where(User.email == user.email, User.provider == user.provider)).first()
    if is_existing_user:
        return is_existing_user
    
    random_password = generate_random_password()
    password_digest = get_password_hash(random_password)
    extra_data = {"password_digest": password_digest}
    db_user = User.model_validate(user, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
    
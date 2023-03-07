from fastapi import APIRouter, HTTPException
from deta import Deta

from passlib.context import CryptContext

import settings
from models.user import UserCreate

deta = Deta(settings.PROJECT_KEY)

users = deta.Base("users")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(
  prefix="/api",
  tags=["users"],
)


@router.get("/user")
async def read_user():
    return {"name": "punpun"}


@router.post("/users/create")
async def create_user(user: UserCreate):
    if user.password != user.password_confirmation:
        raise HTTPException(400, detail="Password and Confirm Password values do not match")
    
    create_user = users.put({
        "name": user.name,
        "email": user.email,
        "password": pwd_context.hash(user.password),
        "password_confirmation": pwd_context.hash(user.password_confirmation),
        "avatar": user.avatar,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    })

    return create_user

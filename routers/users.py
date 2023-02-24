from fastapi import APIRouter
from passlib.context import CryptContext

from models.user import UserCreate

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
    user.password = pwd_context.hash(user.password)
    user.password_confirmation = pwd_context.hash(user.password_confirmation)
    return user
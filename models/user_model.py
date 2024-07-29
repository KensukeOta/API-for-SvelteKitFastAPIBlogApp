from typing import TYPE_CHECKING
from datetime import datetime

from pydantic import EmailStr, field_validator, ValidationInfo
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .post_model import Post


class UserBase(SQLModel):
    name: str = Field(min_length=2, max_length=50)
    email: EmailStr = Field(max_length=254)
    image: str | None = Field(default=None)
    provider: str = Field()
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password_digest: str = Field()

    posts: list["Post"] = Relationship(back_populates="user", cascade_delete=True)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=32)
    password_confirmation: str = Field(min_length=8, max_length=32)

    @field_validator("password_confirmation")
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("passwords do not match")
        return v
    

class OAuthUserCreate(UserBase):
    pass


class UserPublic(UserBase):
    id: int


class UserUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=2, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=254)
    password: str | None = Field(default=None, min_length=8, max_length=32)
    password_confirmation: str | None = Field(default=None, min_length=8, max_length=32)
    image: str | None = Field(default=None)
    provider: str | None = Field(default=None)
    updated_at: datetime = Field(default=datetime.now())

    @field_validator("password_confirmation")
    def passwords_match(cls, v: str, info: ValidationInfo) -> str:
        if "password" in info.data and v != info.data["password"]:
            raise ValueError("passwords do not match")
        return v

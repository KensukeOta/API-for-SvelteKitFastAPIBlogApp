from typing import TYPE_CHECKING
from datetime import datetime

from sqlmodel import Column, Field, Relationship, SQLModel, TEXT

if TYPE_CHECKING:
    from .user_model import User


class PostBase(SQLModel):
    title: str = Field(max_length=50)
    body: str = Field(sa_column=Column(TEXT), max_length=10000)
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default=datetime.now())


class Post(PostBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    user: "User" = Relationship(back_populates="posts")


class PostCreate(PostBase):
    pass


class PostPublic(PostBase):
    id: int


class PostUpdate(SQLModel):
    title: str | None = Field(default=None, max_length=50)
    body: str | None = Field(default=None, sa_column=Column(TEXT), max_length=10000)
    user_id: int | None = Field(default=None, foreign_key="user.id", ondelete="CASCADE")
    updated_at: datetime = Field(default=datetime.now())

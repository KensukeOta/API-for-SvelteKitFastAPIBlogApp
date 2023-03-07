from typing import Union

from fastapi import UploadFile
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=10)
    email: EmailStr
    password: str = Field(min_length=3)
    password_confirmation: str = Field(min_length=3)
    avatar: Union[UploadFile, None] = None
    created_at: str
    updated_at: str
from typing import Union
from datetime import datetime

from fastapi import UploadFile
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    password_confirmation: str
    avatar: Union[UploadFile, None] = None
    created_at: datetime
    updated_at: datetime
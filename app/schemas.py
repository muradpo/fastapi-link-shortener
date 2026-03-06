from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, HttpUrl


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None


class LinkUpdate(BaseModel):
    original_url: HttpUrl


class LinkOut(BaseModel):
    id: int
    original_url: str
    short_code: str
    created_at: datetime
    expires_at: Optional[datetime]
    click_count: int
    last_used_at: Optional[datetime]
    owner_id: Optional[int]

    class Config:
        from_attributes = True


class LinkStats(BaseModel):
    original_url: str
    created_at: datetime
    click_count: int
    last_used_at: Optional[datetime]
    expires_at: Optional[datetime]
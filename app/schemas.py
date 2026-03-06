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

    class Config:
        from_attributes = True


class LinkCreate(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None
    project_name: Optional[str] = None


class LinkUpdate(BaseModel):
    original_url: HttpUrl


class LinkOut(BaseModel):
    id: int
    original_url: HttpUrl
    short_code: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    click_count: int
    last_used_at: Optional[datetime] = None
    owner_id: Optional[int] = None
    project_name: Optional[str] = None

    class Config:
        from_attributes = True


class LinkStats(BaseModel):
    original_url: HttpUrl
    created_at: datetime
    click_count: int
    last_used_at: Optional[datetime] = None

    class Config:
        from_attributes = True
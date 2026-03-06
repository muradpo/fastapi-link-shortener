from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    links = relationship("Link", back_populates="owner")


class Link(Base):
    __tablename__ = "links"

    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(String, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    click_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    owner = relationship("User", back_populates="links")
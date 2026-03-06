from sqlalchemy.orm import Session

from app import models
from app.auth import hash_password
import string
import random
from app.redis_client import redis_client
from datetime import datetime

def get_links_by_project(db, project_name: str):
    return db.query(models.Link).filter(
        models.Link.project_name == project_name
    ).all()

def generate_short_code(length: int = 6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))
def create_link(db, original_url, custom_alias=None, expires_at=None, owner_id=None, project_name=None):

    short_code = custom_alias if custom_alias else generate_short_code()

    link = models.Link(
        original_url=original_url,
        short_code=short_code,
        expires_at=expires_at,
        owner_id=owner_id,
        project_name=project_name
    )

    db.add(link)
    db.commit()
    db.refresh(link)

    return link

def create_user(db: Session, username: str, email: str, password: str):
    password_hash = hash_password(password)

    user = models.User(
        username=username,
        email=email,
        password_hash=password_hash
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()
def get_link_by_code(db, short_code: str):
    return db.query(models.Link).filter(models.Link.short_code == short_code).first()

def update_link(db, short_code: str, new_url: str):

    link = db.query(models.Link).filter(models.Link.short_code == short_code).first()

    if not link:
        return None

    link.original_url = new_url

    db.commit()
    db.refresh(link)

    return link

def delete_link(db, short_code: str):

    link = db.query(models.Link).filter(models.Link.short_code == short_code).first()

    if not link:
        return False

    db.delete(link)
    db.commit()

    return True

def find_links_by_url(db, original_url: str):

    return db.query(models.Link).filter(models.Link.original_url == original_url).all()

def get_cached_original_url(short_code: str):
    return redis_client.get(f"short:{short_code}")


def set_cached_original_url(short_code: str, original_url: str):
    redis_client.set(f"short:{short_code}", original_url)


def delete_cached_original_url(short_code: str):
    redis_client.delete(f"short:{short_code}")

from datetime import datetime


def get_link_by_alias(db, short_code: str):
    return db.query(models.Link).filter(models.Link.short_code == short_code).first()


def delete_expired_links(db):
    expired_links = db.query(models.Link).filter(
        models.Link.expires_at.isnot(None),
        models.Link.expires_at < datetime.utcnow()
    ).all()

    for link in expired_links:
        delete_cached_original_url(link.short_code)
        db.delete(link)

    db.commit()


def get_expired_links(db):
    return db.query(models.Link).filter(
        models.Link.expires_at != None,
        models.Link.expires_at < datetime.utcnow()
    ).all()

def get_user_links(db, user_id):
    return db.query(models.Link).filter(
        models.Link.owner_id == user_id
    ).all()

from datetime import datetime, timedelta

def delete_unused_links(db, days: int = 30):
    threshold = datetime.utcnow() - timedelta(days=days)

    links = db.query(models.Link).filter(
        models.Link.last_used_at != None,
        models.Link.last_used_at < threshold
    ).all()

    for link in links:
        db.delete(link)

    db.commit()

    return len(links)

from datetime import datetime

def get_expired_links(db):
    return db.query(models.Link).filter(
        models.Link.expires_at != None,
        models.Link.expires_at < datetime.utcnow()
    ).all()
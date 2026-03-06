from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine
from app import models, schemas, crud
from app.dependencies import get_db, get_current_user
from app.auth import verify_password, create_access_token
from fastapi.responses import RedirectResponse
from datetime import datetime
from fastapi.security import OAuth2PasswordRequestForm
app = FastAPI(title="Link Shortener")

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "Link shortener service running"}


@app.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = crud.get_user_by_username(db, user.username)

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    return crud.create_user(db, user.username, user.email, user.password)


@app.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_username(db, form_data.username)

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.username})

    return {"access_token": token, "token_type": "bearer"}
@app.post("/links/shorten", response_model=schemas.LinkOut)
def shorten_link(link: schemas.LinkCreate, db: Session = Depends(get_db)):

    crud.delete_expired_links(db)

    if link.custom_alias:
        existing_link = crud.get_link_by_alias(db, link.custom_alias)
        if existing_link:
            raise HTTPException(status_code=400, detail="Custom alias already exists")

    new_link = crud.create_link(
        db=db,
        original_url=str(link.original_url),
        custom_alias=link.custom_alias,
        expires_at=link.expires_at
    )

    return new_link

@app.get("/links/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):

    crud.delete_expired_links(db)

    cached_url = crud.get_cached_original_url(short_code)
    if cached_url:
        link = crud.get_link_by_code(db, short_code)
        if link:
            link.click_count += 1
            link.last_used_at = datetime.utcnow()
            db.commit()
        return RedirectResponse(url=cached_url, status_code=302)

    link = crud.get_link_by_code(db, short_code)

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    link.click_count += 1
    link.last_used_at = datetime.utcnow()
    db.commit()

    crud.set_cached_original_url(short_code, link.original_url)

    return RedirectResponse(url=link.original_url, status_code=302)

@app.get("/links/{short_code}/stats", response_model=schemas.LinkStats)
def get_link_stats(short_code: str, db: Session = Depends(get_db)):

    crud.delete_expired_links(db)

    link = crud.get_link_by_code(db, short_code)

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    return link

@app.put("/links/{short_code}", response_model=schemas.LinkOut)
def update_link(
    short_code: str,
    link_update: schemas.LinkUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    crud.delete_expired_links(db)

    link = crud.get_link_by_code(db, short_code)

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated_link = crud.update_link(db, short_code, str(link_update.original_url))
    crud.delete_cached_original_url(short_code)

    return updated_link

@app.delete("/links/{short_code}")
def delete_link(
    short_code: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    crud.delete_expired_links(db)

    link = crud.get_link_by_code(db, short_code)

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    if link.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    success = crud.delete_link(db, short_code)

    if not success:
        raise HTTPException(status_code=404, detail="Link not found")

    crud.delete_cached_original_url(short_code)

    return {"message": "Link deleted"}

@app.get("/links/search", response_model=list[schemas.LinkOut])
def search_links(original_url: str, db: Session = Depends(get_db)):

    crud.delete_expired_links(db)

    links = crud.find_links_by_url(db, original_url)

    return links

@app.post("/links/shorten/auth", response_model=schemas.LinkOut)
def shorten_link_auth(
    link: schemas.LinkCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    crud.delete_expired_links(db)

    if link.custom_alias:
        existing_link = crud.get_link_by_alias(db, link.custom_alias)
        if existing_link:
            raise HTTPException(status_code=400, detail="Custom alias already exists")

    new_link = crud.create_link(
        db=db,
        original_url=str(link.original_url),
        custom_alias=link.custom_alias,
        expires_at=link.expires_at,
        owner_id=current_user.id
    )

    return new_link
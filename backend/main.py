import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from dotenv import load_dotenv

load_dotenv()

from database import get_db, engine, Base
import models
import cache
import tasks
import utils
import schemas

app = FastAPI(title="URL Shortener")

# Create tables on startup (works for local/dev)
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)

BASE_URL = os.getenv("BASE_URL")
PORT = os.getenv("PORT", "8000")



@app.post("/api/create", response_model=schemas.CreateResponse)
def create_short(payload: schemas.CreateRequest, db: Session = Depends(get_db)):
    original = str(payload.url)   # ✅ Convert HttpUrl → str

    # Generate a unique short_id
    for _ in range(10):
        short = utils.generate_short_id()
        exists = db.query(models.URL).filter(models.URL.short_id == short).first()
        if not exists:
            break
    else:
        raise HTTPException(status_code=500, detail="Unable to generate unique short id")

    url_obj = models.URL(short_id=short, original_url=original)
    db.add(url_obj)
    db.commit()
    db.refresh(url_obj)

    cache.set_to_cache(short, original)

    # if "localhost" in BASE_URL:
    #     short_url = f"{BASE_URL}:{PORT}/{short}"
    # else:
    #     short_url = f"{BASE_URL}/{short}"
    from urllib.parse import urlparse

    parsed = urlparse(BASE_URL)
    if parsed.port is None and PORT not in ("80", "443"):
        short_url = f"{BASE_URL}:{PORT}/{short}"
    else:
        short_url = f"{BASE_URL}/{short}"

    return schemas.CreateResponse(short_url=short_url)


@app.get("/{short_id}")
def redirect_short(short_id: str, db: Session = Depends(get_db)):
    # try cache
    original = cache.get_from_cache(short_id)
    if original:
        # record asynchronously
        tasks.record_click.delay(short_id)
        return RedirectResponse(original)

    obj = db.query(models.URL).filter(models.URL.short_id == short_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Short URL not found")

    cache.set_to_cache(short_id, obj.original_url)
    tasks.record_click.delay(short_id)
    return RedirectResponse(obj.original_url)

@app.get("/api/analytics/{short_id}", response_model=schemas.AnalyticsResponse)
def analytics(short_id: str, db: Session = Depends(get_db)):
    obj = db.query(models.URL).filter(models.URL.short_id == short_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Short URL not found")
    return schemas.AnalyticsResponse(
        original_url=obj.original_url,
        clicks=obj.click_count or 0,
        created_at=obj.created_at.isoformat()
    )

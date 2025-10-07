import os
from celery import Celery
from sqlalchemy.orm import sessionmaker
from database import engine
from models import URL
from dotenv import load_dotenv

load_dotenv()

BROKER = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
BACKEND = os.getenv("CELERY_RESULT_BACKEND", BROKER)

celery_app = Celery("tasks", broker=BROKER, backend=BACKEND)

SessionLocal = sessionmaker(bind=engine)

@celery_app.task(name="tasks.record_click")
def record_click(short_id: str):
    db = SessionLocal()
    try:
        obj = db.query(URL).filter(URL.short_id == short_id).first()
        if obj:
            obj.click_count = (obj.click_count or 0) + 1
            db.add(obj)
            db.commit()
    finally:
        db.close()

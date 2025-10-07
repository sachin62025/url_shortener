@echo off
echo ---------- Starting URL Shortener services...

call venv\Scripts\activate

echo ---------- Starting FastAPI backend...
start cmd /k "cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo ---------- Starting Celery (solo mode for Windows)...
start cmd /k "cd backend && celery -A tasks.celery_app worker --loglevel=info -P solo"

echo ---------- Starting Flask frontend...
set BACKEND_URL=http://10.95.193.234:8000
start cmd /k "cd frontend && flask run --host=0.0.0.0 --port=5000"

echo ---------- All services started!
echo Frontend:  http://10.95.193.234:5000
echo Backend:   http://10.95.193.234:8000/docs

#!/bin/bash
# Run URL Shortener locally (backend + celery + frontend)
# Usage: bash run_local.sh

echo "🚀 Starting Redis (make sure it's already running in Docker or local)..."
echo "---------------------------------------"

# Activate virtual environment
source venv/bin/activate

# Start backend (FastAPI)
echo "⚙️ Starting FastAPI backend..."
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Start Celery worker
echo "📊 Starting Celery worker..."
celery -A tasks.celery_app worker --loglevel=info &
CELERY_PID=$!

# Start frontend
cd ../frontend
export BACKEND_URL=http://10.95.193.234:8000
echo "🌐 Starting Flask frontend..."
flask run --host=0.0.0.0 --port=5000 &
FRONTEND_PID=$!

echo "✅ All services running!"
echo "Frontend:  http://10.95.193.234:5000"
echo "Backend:   http://10.95.193.234:8000/docs"
echo "---------------------------------------"

# Keep script running until you press Ctrl+C
trap "kill $BACKEND_PID $CELERY_PID $FRONTEND_PID" EXIT
wait

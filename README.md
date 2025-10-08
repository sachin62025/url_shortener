# URL Shortener Service

### Objective

A production-ready **URL Shortener** (like Bitly) built using **FastAPI**, **Flask**, **PostgreSQL**, **Redis**, **Celery**, and **Nginx**.
It supports fast link shortening, redirection, caching, analytics, and asynchronous click tracking.

## 1. System Overview

A **user enters a long URL**, and the system returns a short link like:

```
Input: https://www.amazon.com/gp/product/B01N5IB20Q
Output: https://short.ly/xYz12A
```

When anyone visits that short link, they are **redirected to the original URL**, while **analytics are tracked** asynchronously.

## Features

- Generate short URLs instantly
- Fast redirection with Redis cache
- Track click counts (asynchronously with Celery)
- REST API built with FastAPI
- Simple Flask + Jinja2 frontend
- Full Docker Compose support (one command deployment)
- Automated test script (`test_app.py`) for validation

---

---

## Architecture Diagram

```
[User / Browser]
        │
        ▼
  ┌──────────────┐
  │  Nginx Proxy │   ← load balancing & routing
  └──────────────┘
        │
        ├──► /        → Flask Frontend (Port 5000)
        └──► /api/... → FastAPI Backend (Port 8000)
  
  ┌─────────────────────────────────┐
  │ PostgreSQL  →  Permanent Storage│
  ├─────────────────────────────────┤
  │ Redis       →  Caching Layer    │
  ├─────────────────────────────────┤
  │ Celery      →  Async Analytics  │
  └─────────────────────────────────┘
```

---

## Core Components

| Component                  | Tech Stack              | Purpose                                                   |
| -------------------------- | ----------------------- | --------------------------------------------------------- |
| **Frontend**         | Flask + Jinja2          | Simple UI for creating and viewing short links            |
| **Backend**          | FastAPI                 | Exposes REST API for URL creation, redirecting, analytics |
| **Database**         | PostgreSQL              | Stores mapping of short ↔ long URLs                      |
| **Cache**            | Redis                   | Caches short URL lookups for faster redirects             |
| **Queue**            | Celery + Redis broker   | Handles analytics (click count, logs) asynchronously      |
| **Proxy**            | Nginx                   | Routes traffic to frontend/backend and handles SSL        |
| **Containerization** | Docker + Docker Compose | Run all services easily in isolated environments          |

## Environment Variables (`.env`)

```env
POSTGRES_DB=url_shortener
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin
POSTGRES_HOST=db
POSTGRES_PORT=5432
DATABASE_URL=postgresql+psycopg2://admin:admin@db:5432/url_shortener  # for local direct sqlite:///./url_shortener.db

REDIS_URL=redis://redis:6379/0
BASE_URL=http://localhost:8080
PORT=8000

CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/1
```

## Run Locally (without Docker)

### Clone the repository

```bash
git clone https://github.com/sachin62025/url_shortener.git
cd url_shortener
```

### Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate 
```

### Install dependencies

```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### Setup database

```bash
python backend/create_tables.py ## direct create
```

### Start services

```bash
# Start Redis manually (or via Docker) 
redis-server
```

# Start Application direct

```
run_local.bat
```

### Access app

- Frontend → http://localhost:5000
- API Docs → http://localhost:8000/docs

## Run with Docker (recommended)

### Build & start containers

```bash
docker-compose up --build
docker-compose ps
docker-compose logs -f
```

## Access app

- Frontend → http://localhost:5000
- API Docs → http://localhost:8000/docs

## Database Schema (PostgreSQL)

**Table: `urls`**

| Column       | Type               | Description   |
| ------------ | ------------------ | ------------- |
| id           | SERIAL PRIMARY KEY | Auto ID       |
| short_id     | VARCHAR(10) UNIQUE | Short code    |
| original_url | TEXT               | Long URL      |
| created_at   | TIMESTAMP          | Creation date |
| click_count  | INTEGER DEFAULT 0  | Total clicks  |

---

## Redis Cache Design

**Key** → short_id**Value** → original_url

- On redirect request:
  - Check Redis.
  - If **hit**, redirect instantly.
  - If **miss**, fetch from DB → cache → redirect.


---

## Folder Structure

```
url_shortener/
├── frontend/
│   ├── app.py
│   ├── templates/
│   │   ├── index.html
│   │   └── result.html
│   └── Dockerfile
│
├── backend/
│   ├── main.py
│   ├── models.py
│   ├── database.py
│   ├── cache.py
│   ├── tasks.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── test/
├── nginx.conf
├── docker-compose.yml
└── README.md
```

---

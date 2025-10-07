# URL Shortener Service

### Objective

Design and implement a **scalable URL Shortener system** that converts long URLs into short links and redirects users efficiently.
This project demonstrates **backend architecture, caching, async task handling, and containerized deployment**.

---

## 1. System Overview

A **user enters a long URL**, and the system returns a short link like:

```
Input: https://www.amazon.com/gp/product/B01N5IB20Q
Output: https://short.ly/xYz12A
```

When anyone visits that short link, they are **redirected to the original URL**, while **analytics are tracked** asynchronously.

---

## 2. Architecture Diagram

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
  
  ┌────────────────────────────┐
  │ PostgreSQL  →  Permanent Storage│
  ├────────────────────────────┤
  │ Redis       →  Caching Layer   │
  ├────────────────────────────┤
  │ Celery      →  Async Analytics │
  └────────────────────────────┘
```

---

## 3. Core Components

| Component                  | Tech Stack              | Purpose                                                   |
| -------------------------- | ----------------------- | --------------------------------------------------------- |
| **Frontend**         | Flask + Jinja2          | Simple UI for creating and viewing short links            |
| **Backend**          | FastAPI                 | Exposes REST API for URL creation, redirecting, analytics |
| **Database**         | PostgreSQL              | Stores mapping of short ↔ long URLs                      |
| **Cache**            | Redis                   | Caches short URL lookups for faster redirects             |
| **Queue**            | Celery + Redis broker   | Handles analytics (click count, logs) asynchronously      |
| **Proxy**            | Nginx                   | Routes traffic to frontend/backend and handles SSL        |
| **Containerization** | Docker + Docker Compose | Run all services easily in isolated environments          |

---

## 4. Functional Requirements

✅ **Core Features**

1. User submits a long URL → gets back a short URL.
2. Visiting the short URL redirects to the original link.
3. Each visit increments a click count asynchronously.
4. Display analytics (number of clicks, creation date).

✅ **Additional (Optional)**

- Expiry time for short URLs.
- User authentication for managing links.
- Custom alias (user-defined short codes).

---

## 5. API Design (FastAPI)

### Create Short URL

**POST /api/create**

```json
Request:
{
  "url": "https://example.com/my-long-link"
}

Response:
{
  "short_url": "https://short.ly/aB9xYz"
}
```

### Redirect to Original

**GET /{short_id}**

- Redirects to original URL if found.
- Increments analytics count asynchronously.

### Get Analytics

**GET /api/analytics/{short_id}**

```json
Response:
{
  "original_url": "https://example.com/my-long-link",
  "clicks": 124,
  "created_at": "2025-10-07T14:22:00"
}
```

---

## 6. Database Schema (PostgreSQL)

**Table: `urls`**

| Column       | Type               | Description   |
| ------------ | ------------------ | ------------- |
| id           | SERIAL PRIMARY KEY | Auto ID       |
| short_id     | VARCHAR(10) UNIQUE | Short code    |
| original_url | TEXT               | Long URL      |
| created_at   | TIMESTAMP          | Creation date |
| click_count  | INTEGER DEFAULT 0  | Total clicks  |

---

## 7. Redis Cache Design

**Key** → short_id**Value** → original_url

- On redirect request:
  - Check Redis.
  - If **hit**, redirect instantly.
  - If **miss**, fetch from DB → cache → redirect.

---

## 8. Celery Queue (Asynchronous Analytics)

Celery Task Example:

```python
@celery.task
def record_click(short_id):
    db.increment_click(short_id)
```

When a user hits `/{short_id}`:

```python
@app.get("/{short_id}")
def redirect_to_url(short_id: str):
    url = redis.get(short_id) or db.get_url(short_id)
    if url:
        record_click.delay(short_id)
        return RedirectResponse(url)
    raise HTTPException(status_code=404)
```

---

## 9. Flask Frontend

**index.html** — Input form for long URL
**result.html** — Displays short link

Flask routes:

```python
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        long_url = request.form["url"]
        response = requests.post("http://backend:8000/api/create", json={"url": long_url})
        short_url = response.json()["short_url"]
        return render_template("result.html", short_url=short_url)
    return render_template("index.html")
```

---

## 10. Docker Compose Setup

**docker-compose.yml**

```yaml
version: '3.9'
services:
  frontend:
    build: ./frontend
    ports:
      - "5000:5000"

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: url_shortener
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin

  redis:
    image: redis:alpine

  celery:
    build: ./backend
    command: celery -A tasks worker --loglevel=info
    depends_on:
      - backend
      - redis

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
    depends_on:
      - frontend
      - backend
```

---

## 11. Nginx Configuration

**nginx.conf**

```nginx
events {}

http {
    upstream flask_app {
        server frontend:5000;
    }

    upstream fastapi_app {
        server backend:8000;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://flask_app;
        }

        location /api/ {
            proxy_pass http://fastapi_app;
        }
    }
}
```

---

## 12. Folder Structure

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
├── nginx.conf
├── docker-compose.yml
└── README.md
```

---

## 13. What You’ll Learn

| Concept                          | Skill Developed                  |
| -------------------------------- | -------------------------------- |
| **API Design**             | Using FastAPI for REST APIs      |
| **Frontend Integration**   | Flask + Jinja2 with backend      |
| **Caching**                | Redis for fast URL lookups       |
| **Database Design**        | SQL schema & indexing            |
| **Async Processing**       | Celery tasks for analytics       |
| **Containerization**       | Multi-service Docker setup       |
| **Load Balancing**         | Nginx proxy configuration        |
| **System Design Thinking** | Multi-tier scalable architecture |

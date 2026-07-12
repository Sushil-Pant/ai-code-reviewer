# Deployment Guide — AI Code Reviewer

## Table of Contents
1. [Local Development](#1-local-development)
2. [Docker Deployment](#2-docker-deployment)
3. [Cloud Deployment — Render](#3-cloud-deployment--render)
4. [Cloud Deployment — Railway](#4-cloud-deployment--railway)
5. [Cloud Deployment — VPS (Ubuntu)](#5-cloud-deployment--vps-ubuntu)
6. [Environment Variables Reference](#6-environment-variables-reference)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Local Development

### Prerequisites
- Python 3.10+
- Google Gemini API key ([get one free](https://aistudio.google.com/app/apikey))

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ai-code-reviewer.git
cd ai-code-reviewer

# 2. Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 3. Run with the startup script (Linux/Mac)
chmod +x run.sh
./run.sh

# Windows users:
run.bat
```

**Manual setup (if script fails):**

```bash
# Terminal 1 — Backend
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2 — Frontend
cd frontend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:8501        |
| Backend  | http://localhost:8000        |
| API Docs | http://localhost:8000/docs   |

---

## 2. Docker Deployment

### Prerequisites
- Docker Desktop installed and running
- Docker Compose v2+

### Steps

```bash
# 1. Set up .env
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# 2. Build and start all services
docker compose up --build

# 3. Run in background (detached)
docker compose up --build -d

# 4. View logs
docker compose logs -f

# 5. Stop services
docker compose down

# 6. Stop and remove volumes (clears database)
docker compose down -v
```

**Verify running containers:**
```bash
docker compose ps
```

| Service  | Container Name                  | Port  |
|----------|---------------------------------|-------|
| Backend  | ai_code_reviewer_backend        | 8000  |
| Frontend | ai_code_reviewer_frontend       | 8501  |

---

## 3. Cloud Deployment — Render

Render offers a **free tier** perfect for student projects.

### Deploy Backend (FastAPI)

1. Go to [render.com](https://render.com) → **New** → **Web Service**
2. Connect your GitHub repository
3. Configure:
   - **Name:** `ai-code-reviewer-api`
   - **Root Directory:** `backend`
   - **Runtime:** Python 3.11
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add Environment Variables:
   - `GEMINI_API_KEY` → your key
   - `SECRET_KEY` → random 64-char string
   - `DATABASE_URL` → `sqlite:///./ai_code_reviewer.db`
5. Click **Deploy**

### Deploy Frontend (Streamlit)

1. **New** → **Web Service**
2. Configure:
   - **Name:** `ai-code-reviewer-frontend`
   - **Root Directory:** `frontend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
3. Add Environment Variable:
   - `API_BASE_URL` → `https://ai-code-reviewer-api.onrender.com/api`

> **Note:** The frontend now automatically reads `API_BASE_URL` from environment variables, so you do not need to modify `frontend/app.py` directly!

---

## 4. Cloud Deployment — Railway

Railway gives $5/month free credits.

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Deploy backend
cd backend
railway init
railway up

# Deploy frontend
cd ../frontend
railway init
railway up
```

Set environment variables in the Railway dashboard under each service's Variables tab.

---

## 5. Cloud Deployment — VPS (Ubuntu)

For a DigitalOcean/AWS/GCP Ubuntu server.

```bash
# 1. SSH into your server
ssh ubuntu@your-server-ip

# 2. Install dependencies
sudo apt update && sudo apt install -y python3 python3-pip python3-venv nginx git

# 3. Clone project
git clone https://github.com/yourusername/ai-code-reviewer.git
cd ai-code-reviewer

# 4. Set up .env
cp .env.example .env
nano .env   # Add your GEMINI_API_KEY

# 5. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# 6. Deploy with Docker Compose
docker compose up -d --build

# 7. Set up Nginx reverse proxy
sudo nano /etc/nginx/sites-available/ai-code-reviewer
```

**Nginx config:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ai-code-reviewer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# 8. (Optional) Add HTTPS with Certbot
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

---

## 6. Environment Variables Reference

| Variable                    | Required | Default              | Description                        |
|-----------------------------|----------|----------------------|------------------------------------|
| `GEMINI_API_KEY`            | ✅ Yes   | —                    | Google Gemini API key              |
| `SECRET_KEY`                | ✅ Yes   | —                    | JWT signing secret (64+ chars)     |
| `DATABASE_URL`              | No       | `sqlite:///./ai_code_reviewer.db` | Database connection URL |
| `DEBUG`                     | No       | `False`              | Enable debug mode                  |
| `GEMINI_MODEL`              | No       | `gemini-1.5-pro`     | Gemini model version               |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No     | `1440` (24h)         | JWT token lifetime                 |
| `MAX_CODE_LENGTH`           | No       | `50000`              | Max characters per review          |

---

## 7. Troubleshooting

### Backend won't start
```bash
# Check logs
uvicorn main:app --reload --log-level debug

# Verify imports
cd backend && python -c "from main import app; print('OK')"
```

### "Cannot connect to backend"
- Ensure the backend is running on port 8000
- Check `API_BASE` in `frontend/app.py` matches your backend URL
- If using Docker, services communicate via the `app_network`

### Gemini API errors
- Verify `GEMINI_API_KEY` is set correctly in `.env`
- Check your quota at [Google AI Studio](https://aistudio.google.com)
- The free tier allows 15 requests/minute

### Database errors
```bash
cd backend
python -c "from database.db import init_db; init_db(); print('DB OK')"
```

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 8501
lsof -ti:8501 | xargs kill -9
```

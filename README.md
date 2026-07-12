# 🔍 AI Code Reviewer

> **An intelligent, AI-powered code review web application built with FastAPI, Streamlit, and Google Gemini AI.**
> Built as a 6-week summer training project — strong enough for a viva and a GitHub portfolio.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 **AI Analysis** | Powered by Google Gemini 1.5 Pro |
| 🐛 **Bug Detection** | Logic errors, null pointers, off-by-one errors |
| 🔒 **Security Scan** | SQL injection, XSS, buffer overflows, hardcoded secrets |
| ⚡ **Performance Review** | Algorithm efficiency, memory leaks, complexity |
| 👃 **Code Smells** | Dead code, duplication, magic numbers |
| 📏 **Standards Check** | PEP 8, ESLint, Java conventions, C++ best practices |
| 🏆 **Score System** | Overall, Security, Performance, Maintainability (0–100) |
| ✨ **Improved Code** | AI-generated fixed version of your code |
| 📜 **Review History** | Every review saved and searchable |
| 📊 **Dashboard** | Analytics, charts, language breakdown |
| 🔐 **Auth System** | JWT-based register/login |
| 🐳 **Docker Ready** | One-command deployment |

---

## 🖥️ Screenshots

### Code Review Page
```
┌─────────────────────────────────────────────────────────────┐
│  🔍 AI Code Review                                          │
│  ─────────────────────────────────────────────────────────  │
│  Language: [🐍 Python ▼]                                    │
│  ┌───────────────────────────────────┐                      │
│  │  def login(user, pwd):            │   💡 What's Analyzed │
│  │      query = f"SELECT * FROM      │   🐛 Bugs            │
│  │      users WHERE user='{user}'"   │   🔒 Security        │
│  │      ...                          │   ⚡ Performance     │
│  └───────────────────────────────────┘   👃 Code Smells     │
│  [🚀 Analyze Code]                       📏 Standards       │
└─────────────────────────────────────────────────────────────┘

┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐
│ Overall  │ │ Security │ │   Perf.  │ │ Maintainability  │
│    42    │ │    15    │ │    70    │ │       60         │
└──────────┘ └──────────┘ └──────────┘ └──────────────────┘

🔴 [High] Security — SQL Injection vulnerability detected
   in login() function on line 3. User input is directly
   interpolated into SQL query string.
   Fix: Use parameterised queries: cursor.execute(
        "SELECT * FROM users WHERE user=?", (user,))
```

### Dashboard
```
┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│ Reviews  │ │ Avg Score│ │  Issues  │ │  High 🔴 │
│    24    │ │   73.5   │ │   187    │ │    31    │
└──────────┘ └──────────┘ └──────────┘ └──────────┘

[Bar Chart: Avg Scores]     [Pie: Language Distribution]
 Overall  ████████ 73.5       🐍 Python    50%
 Security ██████   60.2       ⚡ JS        25%
 Perf.    █████████ 80.1      ☕ Java      15%
 Maint.   ████████  75.3      ⚙️ C++       10%
```

---

## 🏗️ Project Structure

```
ai-code-reviewer/
│
├── backend/                    # FastAPI backend
│   ├── main.py                 # App entry point, CORS, routers
│   ├── alembic.ini             # Database migration config
│   ├── requirements.txt
│   │
│   ├── database/
│   │   └── db.py               # SQLAlchemy models + session
│   │
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response schemas
│   │
│   ├── routers/
│   │   ├── auth.py             # /api/auth/* (register, login, me)
│   │   ├── review.py           # /api/review/* (analyze, history, get)
│   │   └── dashboard.py        # /api/dashboard/stats
│   │
│   ├── services/
│   │   ├── gemini_service.py   # Gemini AI integration + prompt engineering
│   │   ├── auth_service.py     # JWT, bcrypt, user CRUD
│   │   └── review_service.py   # Business logic, DB operations
│   │
│   ├── utils/
│   │   ├── config.py           # Pydantic settings (reads .env)
│   │   └── dependencies.py     # FastAPI auth dependency
│   │
│   └── migrations/             # Alembic DB migrations
│       ├── env.py
│       └── versions/
│           └── 001_initial_schema.py
│
├── frontend/                   # Streamlit frontend
│   ├── app.py                  # Complete UI (login, review, dashboard, history)
│   ├── requirements.txt
│   └── .streamlit/
│       └── config.toml         # Dark theme configuration
│
├── docker/
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
│
├── docs/
│   ├── ARCHITECTURE.md         # System design + DB schema + flow diagrams
│   ├── DEPLOYMENT_GUIDE.md     # Local, Docker, Render, Railway, VPS
│   └── 6_WEEK_PLAN.md          # Training schedule + viva prep
│
├── docker-compose.yml
├── run.sh                      # Linux/Mac one-command startup
├── run.bat                     # Windows one-command startup
├── .env.example                # Environment variable template
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10+
- Google Gemini API key → [Get it free here](https://aistudio.google.com/app/apikey)

### 2. Clone & Configure
```bash
git clone https://github.com/yourusername/ai-code-reviewer.git
cd ai-code-reviewer

# Copy and fill in your API key
cp .env.example .env
nano .env   # Set GEMINI_API_KEY=your-actual-key
```

### 3. Run (Linux / Mac)
```bash
chmod +x run.sh
./run.sh
```

### 3. Run (Windows)
```bash
run.bat
```

### 3. Run with Docker
```bash
docker compose up --build
```

### 4. Open the App
| Service  | URL |
|---|---|
| 🌐 Frontend | http://localhost:8501 |
| 🔌 Backend API | http://localhost:8000 |
| 📚 API Docs | http://localhost:8000/docs |

---

## 🔌 API Reference

### Authentication
```
POST /api/auth/register    Register new user
POST /api/auth/login       Login, get JWT token
GET  /api/auth/me          Get current user profile
```

### Code Review
```
POST   /api/review/analyze       Submit code for AI review
GET    /api/review/history       Get all past reviews (paginated)
GET    /api/review/{id}          Get one review with full details
DELETE /api/review/{id}          Delete a review
```

### Dashboard
```
GET /api/dashboard/stats    Aggregated stats for dashboard
```

### Example Request
```bash
# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "secret123"}'

# Analyze code (use token from login)
curl -X POST http://localhost:8000/api/review/analyze \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "python",
    "code": "def add(a, b):\n    return a + b"
  }'
```

### Example AI Response
```json
{
  "id": 42,
  "language": "python",
  "overall_score": 85,
  "security_score": 90,
  "performance_score": 88,
  "maintainability_score": 78,
  "total_issues": 3,
  "high_severity_count": 0,
  "medium_severity_count": 1,
  "low_severity_count": 2,
  "issues": [
    {
      "severity": "Medium",
      "category": "Maintainability",
      "description": "Function lacks type hints and docstring",
      "fix": "def add(a: int | float, b: int | float) -> int | float:\n    \"\"\"Return sum of a and b.\"\"\"\n    return a + b",
      "line_number": 1
    }
  ],
  "improved_code": "def add(a: int | float, b: int | float) -> int | float:\n    \"\"\"Return the sum of two numbers.\"\"\"\n    return a + b"
}
```

---

## 🧠 AI & Prompt Engineering

The Gemini prompt uses a **4-layer structure**:

```
Layer 1: System Context
  "You are a Senior Software Engineer with 15+ years of experience..."

Layer 2: Task Specification
  → 6 analysis dimensions (bugs, security, performance, smells, standards, maintainability)
  → Language-specific guidelines (PEP 8 for Python, ESLint for JS, etc.)
  → Scoring rubric (0-100 with criteria for each band)

Layer 3: User Code
  → Embedded in a language-tagged fenced code block

Layer 4: Output Format
  → Exact JSON schema with field names, types, and constraints
  → "Respond ONLY with valid JSON — no text before or after"
```

**Model Settings:**
- Temperature: `0.3` (low = consistent, structured output)
- Max tokens: `8192` (allows full improved_code generation)
- Model: `gemini-1.5-pro`

---

## 🗄️ Database Schema

```sql
-- Users
CREATE TABLE users (
    id              INTEGER PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name       VARCHAR(100),
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      DATETIME
);

-- Code Reviews
CREATE TABLE code_reviews (
    id                    INTEGER PRIMARY KEY,
    user_id               INTEGER REFERENCES users(id),
    language              VARCHAR(20) NOT NULL,
    original_code         TEXT NOT NULL,
    improved_code         TEXT,
    overall_score         FLOAT,
    security_score        FLOAT,
    performance_score     FLOAT,
    maintainability_score FLOAT,
    total_issues          INTEGER,
    high_severity_count   INTEGER,
    medium_severity_count INTEGER,
    low_severity_count    INTEGER,
    raw_response          TEXT,
    created_at            DATETIME
);

-- Individual Issues
CREATE TABLE review_issues (
    id          INTEGER PRIMARY KEY,
    review_id   INTEGER REFERENCES code_reviews(id),
    severity    VARCHAR(20),   -- High | Medium | Low
    category    VARCHAR(50),   -- Security | Performance | Bug | ...
    description TEXT,
    fix         TEXT,
    line_number INTEGER
);
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| AI Engine | Google Gemini 1.5 Pro | Code analysis and generation |
| Backend | FastAPI (Python) | REST API, async, auto-docs |
| Frontend | Streamlit (Python) | Web UI, no JavaScript needed |
| Database | SQLite + SQLAlchemy | Data persistence, ORM |
| Auth | JWT + bcrypt | Secure authentication |
| Charts | Plotly | Interactive visualizations |
| Migrations | Alembic | Schema version control |
| Containers | Docker + Compose | Reproducible deployment |

---

## 📋 Supported Languages

| Language | Icon | Standard Checked |
|---|---|---|
| Python | 🐍 | PEP 8, type hints |
| JavaScript | ⚡ | ESLint, async patterns |
| Java | ☕ | Java naming, SOLID |
| C++ | ⚙️ | RAII, smart pointers |
| C | 🔧 | Memory safety, pointer checks |

---

## 🐳 Docker

```bash
# Start all services
docker compose up --build

# Run in background
docker compose up -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Stop everything
docker compose down
```

---

## 📦 Deployment

See **[docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)** for:
- Local development setup
- Docker Compose deployment
- Render.com (free hosting)
- Railway deployment
- Ubuntu VPS with Nginx

---

## 📅 6-Week Training Plan

See **[docs/6_WEEK_PLAN.md](docs/6_WEEK_PLAN.md)** for the full week-by-week breakdown including:
- Topics to learn each week
- Hands-on tasks and checkboxes
- Viva Q&A preparation
- GitHub portfolio checklist

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add: my feature"`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — free to use for learning and portfolio projects.

---

## 👨‍💻 Author

Built with ❤️ as a 6-week AI training project.
Powered by Google Gemini AI.

---

*If this project helped you, please give it a ⭐ on GitHub!*

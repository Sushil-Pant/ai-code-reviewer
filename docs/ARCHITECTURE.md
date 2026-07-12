# Architecture — AI Code Reviewer

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                                 │
│                   http://localhost:8501                             │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ HTTP
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   STREAMLIT FRONTEND                                │
│                      frontend/app.py                               │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │  Login /     │  │  Code Review │  │  Dashboard &             │  │
│  │  Register    │  │  Page        │  │  History Pages           │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────┬───────────────────────────────────────────┘
                          │ REST API (JSON)
                          │ Bearer JWT Token
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FASTAPI BACKEND                                  │
│                    backend/main.py                                  │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                      API ROUTERS                              │  │
│  │  /api/auth/*   /api/review/*   /api/dashboard/*              │  │
│  └───────────────────────┬───────────────────────────────────────┘  │
│                          │                                          │
│  ┌───────────────────────▼───────────────────────────────────────┐  │
│  │                     SERVICES LAYER                            │  │
│  │  auth_service.py   review_service.py   gemini_service.py     │  │
│  └──────────┬─────────────────────────────────┬─────────────────┘  │
│             │                                 │                     │
│  ┌──────────▼──────────┐         ┌────────────▼───────────────────┐ │
│  │   SQLite Database   │         │      Google Gemini AI          │ │
│  │   (SQLAlchemy ORM)  │         │      gemini-1.5-pro            │ │
│  │                     │         │                                │ │
│  │  • users            │         │  Prompt Engineering →          │ │
│  │  • code_reviews     │         │  Structured JSON Response      │ │
│  │  • review_issues    │         │                                │ │
│  └─────────────────────┘         └────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Request Flow

```
User pastes code
      │
      ▼
Streamlit validates input
(language selected, code not empty)
      │
      ▼
POST /api/review/analyze
Authorization: Bearer <JWT>
Body: { code, language }
      │
      ▼
FastAPI auth middleware
verifies JWT → gets user
      │
      ▼
review_service.perform_code_review()
      │
      ├──► gemini_service.analyze_code()
      │         │
      │         ▼
      │    build_review_prompt()
      │    (Prompt Engineering)
      │         │
      │         ▼
      │    Gemini API call
      │    (gemini-1.5-pro)
      │         │
      │         ▼
      │    _parse_response()
      │    Validates + cleans JSON
      │         │
      │    Returns structured dict:
      │    { overall_score, security_score,
      │      performance_score, maintainability_score,
      │      issues[], improved_code }
      │
      ├──► Save CodeReview to SQLite
      ├──► Save each ReviewIssue to SQLite
      │
      ▼
JSON Response → Streamlit
      │
      ▼
Render Score Cards + Gauge Charts
Display Issues (filtered by severity)
Show Improved Code
```

---

## Database Schema

```
┌─────────────────────────────┐
│           users             │
├─────────────────────────────┤
│ id          INTEGER  PK     │
│ username    VARCHAR  UNIQUE │
│ email       VARCHAR  UNIQUE │
│ hashed_password VARCHAR     │
│ full_name   VARCHAR         │
│ is_active   BOOLEAN         │
│ created_at  DATETIME        │
└──────────────┬──────────────┘
               │ 1:N
               ▼
┌─────────────────────────────┐
│        code_reviews         │
├─────────────────────────────┤
│ id               INTEGER PK │
│ user_id          INTEGER FK │
│ language         VARCHAR    │
│ original_code    TEXT       │
│ improved_code    TEXT       │
│ overall_score    FLOAT      │
│ security_score   FLOAT      │
│ performance_score FLOAT     │
│ maintainability_score FLOAT │
│ total_issues     INTEGER    │
│ high_severity_count INTEGER │
│ medium_severity_count INT   │
│ low_severity_count INTEGER  │
│ raw_response     TEXT       │
│ created_at       DATETIME   │
└──────────────┬──────────────┘
               │ 1:N
               ▼
┌─────────────────────────────┐
│        review_issues        │
├─────────────────────────────┤
│ id          INTEGER  PK     │
│ review_id   INTEGER  FK     │
│ severity    VARCHAR         │
│ category    VARCHAR         │
│ description TEXT            │
│ fix         TEXT            │
│ line_number INTEGER         │
└─────────────────────────────┘
```

---

## Prompt Engineering Strategy

The Gemini prompt uses a multi-layer strategy:

```
┌──────────────────────────────────────────────────────────┐
│                  SYSTEM CONTEXT                          │
│  "You are a Senior Software Engineer with 15+ years..."  │
│  "Respond ONLY with valid JSON"                          │
└──────────────────────────────────────────────────────────┘
                          │
┌──────────────────────────────────────────────────────────┐
│               TASK SPECIFICATION                         │
│  • 6 analysis dimensions (bugs, security, perf...)       │
│  • Language-specific guidelines (PEP8, ESLint, etc.)     │
│  • Scoring rubric (0-100 with criteria)                  │
│  • Severity definitions (High/Medium/Low)                │
└──────────────────────────────────────────────────────────┘
                          │
┌──────────────────────────────────────────────────────────┐
│              CODE BLOCK (User Input)                     │
│  ```{language}                                           │
│  {user_code}                                             │
│  ```                                                     │
└──────────────────────────────────────────────────────────┘
                          │
┌──────────────────────────────────────────────────────────┐
│            OUTPUT FORMAT SPECIFICATION                   │
│  • Exact JSON schema with field names                    │
│  • Example values with types                            │
│  • Explicit "no markdown, no preamble" instruction      │
└──────────────────────────────────────────────────────────┘
```

**Temperature:** 0.3 (low = consistent, structured output)
**Max tokens:** 8192 (allows full improved_code generation)

---

## Security Architecture

```
Password Flow:
  plaintext → bcrypt hash (cost=12) → stored in DB
  login → bcrypt.verify() → JWT issued

JWT Flow:
  login → create_access_token(user_id, exp=24h)
  request → OAuth2PasswordBearer → decode_token()
  → get_user_by_id() → inject User into route handler

Ownership Guards:
  Every review query includes: WHERE user_id = current_user.id
  No user can read/delete another user's reviews
```

---

## Technology Choices

| Component        | Technology          | Why                                              |
|------------------|---------------------|--------------------------------------------------|
| AI Engine        | Google Gemini 1.5 Pro | Best code understanding, free tier available   |
| Backend          | FastAPI             | Async, auto-docs, Pydantic validation           |
| Frontend         | Streamlit           | Rapid Python UI, no JS needed                   |
| Database         | SQLite + SQLAlchemy | Zero setup, ORM for clean queries               |
| Auth             | JWT + bcrypt        | Industry standard, stateless                    |
| Charts           | Plotly              | Interactive, dark-theme compatible              |
| Migrations       | Alembic             | Version-controlled schema changes               |
| Deployment       | Docker Compose      | Reproducible environment                        |

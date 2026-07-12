# 6-Week Training Plan — AI Code Reviewer

## Overview
This plan is structured for a summer internship/training program.
Each week builds on the previous. By Week 6 you will have a
complete, deployable AI project for your portfolio and viva.

---

## Week 1 — Foundations & Setup
**Goal:** Understand the tech stack and get the skeleton running.

### Topics to Learn
- Python virtual environments and package management (pip, venv)
- REST API concepts (GET, POST, status codes, JSON)
- FastAPI basics: routes, request/response models, Swagger UI
- SQLite + SQLAlchemy: ORM concepts, models, sessions

### Tasks
- [ ] Install Python 3.11, Git, VS Code
- [ ] Clone/create the project folder structure
- [ ] Create `database/db.py` with User + CodeReview + ReviewIssue models
- [ ] Create `main.py` with a `/health` endpoint
- [ ] Test the API on `http://localhost:8000/docs`
- [ ] Read: What is an ORM? What is a REST API?

### Deliverable
Running FastAPI server with database tables created (`init_db()`).

---

## Week 2 — Authentication System
**Goal:** Users can register, log in, and receive a JWT token.

### Topics to Learn
- Password hashing with bcrypt
- JWT (JSON Web Tokens): structure, signing, expiry
- FastAPI `Depends()` dependency injection
- Pydantic validation: validators, EmailStr

### Tasks
- [ ] Implement `auth_service.py`: `hash_password`, `verify_password`, `create_access_token`
- [ ] Build `/api/auth/register` and `/api/auth/login` endpoints
- [ ] Add `get_current_user` dependency for protected routes
- [ ] Test with Swagger UI: register a user, login, use the token
- [ ] Read: How does JWT work? What is OAuth2?

### Deliverable
Working auth system. Test register + login in Postman/Swagger.

---

## Week 3 — Gemini AI Integration (Core Feature)
**Goal:** Connect to Google Gemini API and get structured code review.

### Topics to Learn
- Google Generative AI Python SDK
- Prompt engineering: system context, few-shot, output format
- JSON parsing and validation in Python
- Error handling for external API calls

### Tasks
- [ ] Get Gemini API key from Google AI Studio
- [ ] Install `google-generativeai` and write `gemini_service.py`
- [ ] Write the prompt template in `build_review_prompt()`
- [ ] Implement `_clean_json_response()` and `_parse_response()`
- [ ] Test with raw Python script first (before wiring into FastAPI)
- [ ] Read: What is prompt engineering? Temperature vs top_p?

### Key Experiment
Try different temperature values (0.1, 0.5, 0.9) and observe how
the consistency of the JSON output changes.

### Deliverable
`gemini_service.analyze_code("print('hello')", "python")` returns valid dict.

---

## Week 4 — Full Backend API
**Goal:** Complete all review endpoints and database storage.

### Topics to Learn
- Async/await in Python and FastAPI
- SQLAlchemy relationships (one-to-many)
- Query filtering, pagination (skip/limit)
- Aggregate queries (AVG, SUM, COUNT, GROUP BY)

### Tasks
- [ ] Implement `review_service.py`: `perform_code_review()`, `get_user_reviews()`, `get_dashboard_stats()`
- [ ] Wire up `/api/review/analyze`, `/api/review/history`, `/api/review/{id}`
- [ ] Implement `/api/dashboard/stats` with all aggregates
- [ ] Test all endpoints in Swagger UI with a real JWT token
- [ ] Read: What is async I/O? Why use it with AI APIs?

### Deliverable
Full API working end-to-end. Submit real code, see stored result in DB.

---

## Week 5 — Streamlit Frontend
**Goal:** Build a polished, professional UI that talks to the backend.

### Topics to Learn
- Streamlit: session state, pages, widgets, caching
- Plotly: bar charts, pie charts, gauge charts
- CSS-in-Streamlit via `st.markdown(unsafe_allow_html=True)`
- API calls from Python using the `requests` library

### Tasks
- [ ] Build login/register page with tabs
- [ ] Build code review page: language selector, code textarea, submit button
- [ ] Render score cards and gauge charts from API response
- [ ] Display issues list with severity badges and expandable fix sections
- [ ] Show improved code with syntax highlighting and download button
- [ ] Build dashboard page with charts and metrics
- [ ] Build history page with expandable review rows
- [ ] Read: Streamlit session_state docs

### Deliverable
Full working UI. End-to-end: paste code → see review results.

---

## Week 6 — Polish, Docker & Deployment
**Goal:** Production-ready project for portfolio and viva.

### Topics to Learn
- Docker: images, containers, volumes, networking
- Docker Compose: multi-service orchestration
- Environment variables and secrets management
- Writing a good README and architecture documentation

### Tasks
- [ ] Write `Dockerfile.backend` and `Dockerfile.frontend`
- [ ] Write `docker-compose.yml`
- [ ] Test `docker compose up --build` locally
- [ ] Deploy backend to Render.com (free tier)
- [ ] Deploy frontend to Render.com
- [ ] Write `README.md` with screenshots
- [ ] Write `ARCHITECTURE.md` with diagrams
- [ ] Create a 5-minute demo video for your GitHub
- [ ] Push everything to GitHub with a clean commit history

### Deliverable
Live deployed app URL + GitHub repo + demo video.

---

## Viva Preparation

### Likely Questions & Answers

**Q: Why did you choose Gemini over OpenAI GPT?**
A: Gemini 1.5 Pro has a large context window (1M tokens), making it
excellent for analyzing large code files. It also has a generous free
tier ideal for a student project.

**Q: How does your prompt engineering work?**
A: I use a structured prompt with four sections: system context
(defining the AI's role), task specification (the six analysis
dimensions), the user's code, and an exact JSON output schema.
Setting temperature to 0.3 ensures consistent structured output.

**Q: How is authentication implemented?**
A: Passwords are hashed with bcrypt (one-way hash). On login, a
JWT token is issued containing the user ID and expiry. Every
protected API route decodes and validates this token using FastAPI's
`Depends()` system.

**Q: What is the database schema?**
A: Three tables: `users` (credentials), `code_reviews` (scores and
metadata per review), and `review_issues` (individual issues in a
1:N relationship with reviews).

**Q: How do you handle Gemini returning invalid JSON?**
A: `_clean_json_response()` strips markdown fences and finds the
JSON boundaries. If `json.loads()` still fails, `_fallback_response()`
returns a safe default structure so the app never crashes.

**Q: How would you scale this to production?**
A: Replace SQLite with PostgreSQL, add Redis for caching frequent
queries, use Celery for async review processing (so the HTTP request
doesn't time out), and deploy behind a load balancer on Kubernetes.

---

## GitHub Portfolio Checklist

- [ ] Clean `README.md` with screenshots and GIF demo
- [ ] Proper `.gitignore` (no `.env`, no `venv/`, no `.db` files)
- [ ] Architecture diagram in `docs/`
- [ ] All code commented and readable
- [ ] At least 10 meaningful git commits (not just one big dump)
- [ ] Live demo link in GitHub description
- [ ] Topics/tags: `python`, `fastapi`, `streamlit`, `gemini-ai`, `code-review`, `machine-learning`

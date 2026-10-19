# Explicite AI — Project Status Checkpoint

> Last updated: 2026-10-19  
> Written by: Claude Code (Sonnet 4.6)  
> Purpose: Resume checkpoint — read this file at the start of the next session.

---

## 1. Repository

| Field | Value |
|-------|-------|
| GitHub remote | https://github.com/Rijulll22/Explicite-AI.git |
| Branch | `main` |
| Latest commit | `a5c6aeac1351e82de22e2b8056353d3abbeadb2e` |
| Commit message | `Replace repository with Explicite AI full-stack application` |
| Git root | `C:\Users\Xpert Origin\Desktop\USABILITY PROJECT` |

> **Note:** The local working tree has significant uncommitted changes (all the work done in the last two sessions). Nothing has been pushed to GitHub yet. The local code is ahead of the remote.

---

## 2. Project Architecture

```
USABILITY PROJECT/
├── backend/          FastAPI + Python 3.14, async SQLAlchemy 2.x, asyncpg
│   ├── app/          Application code (models, schemas, api, services)
│   ├── migrations/   Alembic async migrations
│   ├── tests/        pytest-asyncio test suite (333 tests)
│   ├── venv/         Python virtual environment
│   ├── uploads/      Uploaded source files (runtime)
│   ├── seed.py       Development data seeder
│   └── .env          Local environment config (never commit)
└── frontend/         React 19 + TypeScript + Vite 8 + Tailwind CSS v4
    ├── src/
    │   ├── App.tsx         Root component, NavCtx, screen router
    │   ├── lib/api.ts       All API types and fetch functions
    │   ├── screens/        One file per screen
    │   └── components/     Shared UI components
    └── dist/               Production build output (last built this session)
```

**Key architectural decisions:**
- No frontend routing library — screen navigation via `NavCtx` in `App.tsx` with `useState<Screen>`
- JWT HS256, token stored in `sessionStorage` key `explicite_token`
- API prefix: `/api/v1`
- PostgreSQL `now()` quirk: transaction-time timestamp — use Python-side `datetime.now(timezone.utc)` for reliable ordering
- SQLAlchemy identity map cache: bypass with explicit `SELECT` when freshness matters (used in tutor chat)

---

## 3. Environment Configuration

All configuration lives in `backend/.env`. Variable names (values are never stored here):

| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | Async DSN for PostgreSQL (asyncpg driver), main DB |
| `TEST_DATABASE_URL` | Separate test database DSN |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Docker Compose DB credentials |
| `JWT_SECRET_KEY` | 64-byte hex secret for HS256 signing |
| `JWT_ALGORITHM` | `HS256` |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL (default 60) |
| `CORS_ORIGINS` | Allowed origins (default `http://localhost:8443`) |
| `APP_ENV` | `development` / `production` |
| `UPLOAD_DIR` | Directory for uploaded source files (default `uploads`) |
| `MAX_UPLOAD_BYTES` | Upload size limit (default 10 MB) |
| `ANALYSIS_TIMEOUT_SECONDS` | Semgrep timeout (default 300) |
| `LLM_PROVIDER` | `none` / `anthropic` / `ollama` — controls AI features |
| `ANTHROPIC_API_KEY` | Required when `LLM_PROVIDER=anthropic` |
| `ANTHROPIC_MODEL` | Default `claude-haiku-4-5` |
| `OLLAMA_BASE_URL` | Required when `LLM_PROVIDER=ollama` |
| `OLLAMA_MODEL` | Default `llama3` |
| `LLM_TIMEOUT_SECONDS` | AI call timeout |
| `LLM_MAX_TOKENS` | Max tokens per AI response |

Frontend uses one optional env variable:
- `VITE_API_BASE_URL` — defaults to `http://localhost:8000/api/v1` if unset

---

## 4. Startup Commands

### PostgreSQL (Docker)
```sh
# Start container (port 5434 on host → 5432 in container):
docker run -d --name explicite-db \
  -e POSTGRES_USER=explicite \
  -e POSTGRES_PASSWORD=<your-password> \
  -e POSTGRES_DB=explicite_ai \
  -p 5434:5432 postgres:16

# Create test database:
docker exec -it explicite-db psql -U explicite -c "CREATE DATABASE test_explicite_ai;"
```

### Backend
```sh
cd "C:\Users\Xpert Origin\Desktop\USABILITY PROJECT\backend"
venv\Scripts\activate          # Windows activation
uvicorn app.main:app --reload --port 8000
```
- API base: `http://localhost:8000`
- Health check: `GET http://localhost:8000/health`
- Interactive docs: `http://localhost:8000/docs`

### Frontend
```sh
cd "C:\Users\Xpert Origin\Desktop\USABILITY PROJECT\frontend"
pnpm dev
```
- Dev server: `http://localhost:8443`
- Production build: `pnpm build` (output in `dist/`)

### Run tests
```sh
cd "C:\Users\Xpert Origin\Desktop\USABILITY PROJECT\backend"
venv\Scripts\activate
python -m pytest --ignore=tests/test_slow_integration.py -q
```

---

## 5. Database Migrations

All migrations have been applied. Current head: `a7f3b90d12e8`.

| Revision | File | Status |
|----------|------|--------|
| `18ab260079b1` | `initial_schema.py` | Applied |
| `caf27a49317a` | `add_source_path_to_analysis_jobs.py` | Applied |
| `53ef0c95f7a6` | `add_suggested_fixes_table.py` | Applied |
| `4df931a7000b` | `add_learning_path_resources_table.py` | Applied |
| `e8a4f1b9c253` | `add_user_preferences.py` | Applied |
| `5d7e502760f4` | `add_cvss_vector_and_version_to_findings.py` | Applied |
| `a7f3b90d12e8` | `add_tutor_sessions_and_messages.py` | **Applied — HEAD** |

To verify: `cd backend && venv\Scripts\activate && alembic current`  
Expected output: `a7f3b90d12e8 (head)`

---

## 6. Completed Features

### Core platform
- User authentication (JWT, register, login, logout)
- Project management (create, list, open, membership)
- Source file upload and Semgrep static analysis
- Finding/issue list with severity, CVSS v3.1 scoring, CWE mapping
- Issue detail view with source excerpt and line context
- AI-powered explanations (explain finding, suggested fix, code fix review)
- AI assistant chat (per-project, multi-turn)
- User preferences (email notifications, sort order, AI explain level, appearance)
- Settings screen with theme toggle

### Learning & Tutor (completed this session)
- Learning resources and learning paths
- Learning progress tracking (resources completed, study time)
- Issue-contextual resource recommendations via Semgrep rule key / issue type
- `POST /api/v1/learning/tutor/start` — idempotent session creation (one per user+resource)
- `POST /api/v1/learning/tutor/{session_id}/chat` — multi-turn AI tutor chat
- Conversation persistence in PostgreSQL (TutorSession + TutorMessage tables)
- Cross-user isolation enforced server-side (403 on wrong owner)
- AI unavailable returns 503 but saves user's message
- Frontend: all learning resource cards are clickable and open the AI Tutor screen
- Frontend: TutorSession screen — chat transcript, code block rendering, suggested prompts, Mark Complete, back navigation
- Mark Complete button uses `stopPropagation` so it does not open the tutor

### Test coverage
- 333 backend tests passing, 1 skipped (slow integration test), 1 warning (custom mark)
- Test files: `test_auth`, `test_projects`, `test_analysis`, `test_issues`, `test_source_preview`, `test_cvss_scoring`, `test_ai_service`, `test_learning`, `test_tutor` (15 tutor tests added this session)

### Build / type checks
- TypeScript: 0 errors (`npx tsc --noEmit`)
- Production build: passes (`pnpm build`, output 304 KB JS / 30 KB CSS, built in ~500 ms)

---

## 7. Files Changed This Session (Not Yet Committed)

### Backend
| File | Change |
|------|--------|
| `backend/app/models/learning.py` | Added `TutorSession` and `TutorMessage` models |
| `backend/migrations/versions/a7f3b90d12e8_add_tutor_sessions_and_messages.py` | New migration (applied) |
| `backend/app/schemas/learning.py` | Added tutor request/response schemas |
| `backend/app/services/ai_service.py` | Added `chat_multi_turn()` to all AI providers |
| `backend/app/api/learning.py` | Added two tutor endpoints |
| `backend/tests/test_tutor.py` | 15 new tests (NEW FILE) |
| `backend/app/services/cvss_scoring.py` | Fixed v3.0 version preservation |
| `backend/tests/test_cvss_scoring.py` | Fixed expected CVSS score (9.9 → 9.1) |
| `backend/tests/test_source_preview.py` | Fixed `owner_id` and `ProjectMembership` class name |
| `backend/app/api/issues.py` | Fixed `SourceExcerptResponse` UnboundLocalError |
| `backend/tests/test_ai_service.py` | Fixed mock signature for `json_mode` param |

### Frontend
| File | Change |
|------|--------|
| `frontend/src/App.tsx` | Added `"tutor"` screen, `openTutor()`, `selectedLearningResource` state |
| `frontend/src/lib/api.ts` | Added `ApiTutorMessage`, `ApiTutorSession`, `ApiTutorChatResponse`, `apiStartTutorSession`, `apiTutorChat` |
| `frontend/src/screens/TutorSession.tsx` | NEW FILE — full tutor chat screen |
| `frontend/src/screens/Learning.tsx` | Made all resource cards clickable; Mark Complete stops propagation |

---

## 8. Next Task

**Verify frontend ↔ backend communication end-to-end.**

The backend and frontend have never been tested running together from the current codebase. All tests so far are either unit tests (backend) or build checks (frontend). The integration path has not been exercised.

### Step-by-step verification plan

1. **Start PostgreSQL** — confirm the Docker container is running (`docker ps | findstr explicite-db`)
2. **Start the backend** — `uvicorn app.main:app --reload --port 8000` from `backend/` with venv active
3. **Start the frontend** — `pnpm dev` from `frontend/` (port 8443)
4. **Test login** — open `http://localhost:8443`, log in with seed credentials (`jane.doe@university.ac.uk` / `password`)
5. **Test project navigation** — open a project, navigate to Issues
6. **Test the AI Tutor flow** — go to Learning, click a resource card, verify the tutor screen opens and can send a message (will 503 if `LLM_PROVIDER=none`, which is expected)
7. **Test Mark Complete** — verify it marks without opening the tutor
8. **Monitor browser console and backend logs** for errors

### Known things to check
- CORS: `CORS_ORIGINS` in `.env` must include `http://localhost:8443`
- `VITE_API_BASE_URL` — if unset, defaults to `http://localhost:8000/api/v1` which is correct
- The `SETUP.md` still references migration head `4df931a7000b` (stale — actual head is now `a7f3b90d12e8`); update `SETUP.md` if needed

---

## 9. Known Bugs and Incomplete Items

| Item | Severity | Notes |
|------|----------|-------|
| `SETUP.md` expected migration head is stale | Low | Says `4df931a7000b`; actual head is `a7f3b90d12e8` |
| No proxy configured in Vite | Low | `frontend/.env` or `vite.config.ts` has no `/api` proxy; frontend calls `localhost:8000` directly (CORS must be configured) |
| `AnthropicProvider.chat_multi_turn` uses single-turn workaround | Low | Folds history into a context block; works correctly but does not use Anthropic's native messages array |
| Tutor "Quiz me" is AI-improvised | Info | No structured quiz mode; relies on the model to generate questions from the prompt |
| Conversation history capped at 20 messages | Info | Only last 20 messages sent to AI — older history is in DB but excluded from model context |
| No end-to-end / browser tests | Info | All tests are backend unit/integration tests; no Playwright or similar |
| `frontend/dist/` is in the repo | Info | Built output is tracked; consider adding to `.gitignore` |

---

## 10. Seed Credentials

Safe to use for local development only (created by `python seed.py`):

| Field | Value |
|-------|-------|
| Email | `jane.doe@university.ac.uk` |
| Password | `password` |

Re-run `seed.py` if the database is wiped — it is duplicate-safe.

---

## How to Resume

Open a new Claude Code session in `C:\Users\Xpert Origin\Desktop\USABILITY PROJECT`, then say:

> Read `PROJECT_STATUS.md` and continue from the checkpoint. Start with the next task: verify frontend ↔ backend communication end-to-end.

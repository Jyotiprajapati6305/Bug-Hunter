# Bug Hunter Arena — Phase 1

Bug Hunter Arena is a gamified QA/testing learning platform — think "LeetCode,
but for software testing skills." Testers hunt for bugs in sandboxed
challenges, write bug reports, and earn XP/levels for valid finds.

This repository currently contains **Phase 1**: the core foundation —
authentication, the challenge/bug/XP data model, and a working end-to-end
flow from "browse challenges" to "submit a bug report" to "see XP and level
go up." It is a real, runnable system, not a mockup.

## What's included in Phase 1

- **Backend** (`backend/`): FastAPI + SQLAlchemy 2.0 + Alembic + PostgreSQL +
  JWT auth + Redis + Celery, structured as router -> service -> repository ->
  model.
- **Frontend** (`frontend/`): React + TypeScript + Vite + Tailwind, dark
  monochrome UI (Linear/Vercel/GitHub-dark aesthetic), wired to the real
  backend API (no mock data).
- **Full database schema** for the entire product vision (see below), with
  one comprehensive Alembic migration. Tables for future features
  (leaderboards, achievements, developer reviews, etc.) exist now so later
  phases can build on a stable schema without breaking migrations — but
  there is no API or UI for them yet.
- **Working auth flow**: register, login, refresh (with rotation), logout,
  forgot/reset password.
- **Working challenge flow**: list/filter challenges, start a challenge
  session, submit a bug report tied to that session, get XP awarded
  immediately based on severity, see your level update.
- **Celery worker** wired up and running (used today for a logging-only
  "send email" task — registration and password-reset emails are logged,
  not actually sent, since there's no SMTP provider in Phase 1).
- **Pytest suite** (24 tests) covering auth end-to-end, the XP/level formula,
  and the full challenge -> session -> bug submission -> XP award flow
  against a real (SQLite) database via FastAPI's `TestClient`.

## What's explicitly NOT built yet (future phases)

- Leaderboard pages (table exists: `leaderboards`)
- Analytics charts/dashboards
- Achievements UI (tables exist: `achievements`, `user_achievements`)
- Exploratory/timed challenge mode
- Developer bug-review UI (table exists: `developer_reviews`)
- CI/CD pipeline

These are intentionally scoped out. Their database tables are already
defined and migrated so future phases don't require destructive schema
changes.

## Running it

### Prerequisites
- Docker and Docker Compose

### Quick start

```bash
cp .env.example .env
docker-compose up --build
```

This starts:
- `postgres` (5432) — with a healthcheck; the backend waits for it to be
  healthy before starting.
- `redis` (6379)
- `backend` (8000) — runs `alembic upgrade head` on boot, then starts
  uvicorn.
- `celery_worker` — starts after backend, runs the (currently minimal)
  Celery worker.
- `frontend` (5173) — Vite dev server.

Once it's up:
- API docs: http://localhost:8000/docs
- Frontend: http://localhost:5173

### Seeding demo data

After the stack is up, seed demo users, roles, categories, and sample
challenges:

```bash
docker-compose exec backend python seed.py
```

(Seeding is idempotent — safe to re-run.)

### Demo credentials

| Role      | Email                   | Password    |
|-----------|--------------------------|-------------|
| Admin     | admin@bughunter.dev      | Admin123!   |
| Developer | dev@bughunter.dev        | Dev123!     |
| Tester    | tester@bughunter.dev     | Tester123!  |

Only the `tester` role can submit bug reports (`POST
/api/v1/challenges/{id}/submit-bug` is role-guarded).

## Database schema

A single Alembic migration creates all 25 tables for the full product
vision: `users`, `roles`, `user_profiles`, `challenges`,
`challenge_categories`, `challenge_sessions`, `challenge_submissions`,
`bugs`, `bug_comments`, `bug_attachments`, `test_cases`, `achievements`,
`user_achievements`, `leaderboards`, `notifications`, `activity_logs`,
`audit_logs`, `api_challenges`, `security_challenges`,
`performance_challenges`, `developer_reviews`, `xp_transactions`,
`password_resets`, `email_verifications`, `refresh_tokens`. All tables use
UUID primary keys (except small lookup/junction tables), `created_at` /
`updated_at` timestamps with server defaults, and soft-delete
(`deleted_at`) where applicable.

## XP / leveling formula

Severity -> XP: `critical=100, high=70, medium=50, low=25`. Duplicate or
rejected bugs award 0 XP.

Level thresholds start at the spec's fixed values (`L1=0, L2=100, L3=300,
L4=600, L5=1000`) and continue the same progressively-increasing pattern
beyond level 5 (`delta(n) = 100 * n` XP to go from level `n` to `n+1`). See
`backend/app/services/xp_service.py` for the full implementation and
derivation.

## Running tests locally (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
pytest -q
```

The test suite runs against an in-memory SQLite database (via a
TypeDecorator that maps UUID/JSONB columns to portable types), so it does
not require Postgres to be running.

## Deploying to Render

A `render.yaml` blueprint at the repo root provisions everything: a free
Postgres database, a free Redis instance, the backend (Docker web service),
the Celery worker (Docker background worker), and the frontend (static site
built with Vite).

1. Push this repo to GitHub (already done if you're reading this on GitHub).
2. In the Render dashboard: **New +** -> **Blueprint** -> connect this repo.
   Render reads `render.yaml` and creates all five resources in one go.
3. Wait for `bughunter-backend` to finish deploying, then copy its URL
   (shown at the top of its service page, e.g.
   `https://bughunter-backend-xxxx.onrender.com`).
4. Open `bughunter-frontend` -> Environment, set `VITE_API_BASE_URL` to
   `<backend-url>/api/v1`, then trigger **Manual Deploy** -> **Deploy latest
   commit** (Vite bakes env vars in at build time, so a plain restart isn't
   enough).
5. Copy the frontend's URL, open `bughunter-backend` -> Environment, set
   `CORS_ORIGINS` to `["<frontend-url>"]`, save (this one redeploys
   automatically).
6. Once the backend is live, seed demo data via the Render shell on the
   `bughunter-backend` service: `python seed.py`.

Free-tier notes: Render's free Postgres expires after 90 days, and free web
services spin down after inactivity (cold start ~30-60s on the next
request) — fine for a portfolio demo, not for production traffic.

## Known rough edges

- The frontend's `npm run dev` Docker service mounts the local `frontend/`
  directory as a volume for hot reload; the `node_modules` install baked
  into the image is preserved via an anonymous volume so it isn't shadowed.
- Password-reset and welcome emails are logged via the Celery worker
  (`Would send email to ...`) rather than actually delivered — there is no
  SMTP/email provider integration in Phase 1.
- `docker-compose up --build` was not run in this environment (no Docker
  daemon available here); instead, every component was verified directly:
  Alembic migration apply/downgrade against SQLite, the full pytest suite,
  a live uvicorn server exercised with real HTTP requests through the
  entire challenge -> bug -> XP flow, a live Celery worker boot, and a
  production `vite build` of the frontend. The Dockerfiles and
  docker-compose.yml follow the same commands (`alembic upgrade head` +
  `uvicorn`, `celery worker`, `npm run dev`) that were verified locally.

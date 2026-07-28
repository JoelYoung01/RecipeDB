# Cursor Cloud agent guide

Detailed setup, run, and testing notes for Cursor Cloud agents working in this repo. `AGENTS.md` links here so that this context is only loaded when needed.

This is a single repo containing two services that run together in development:

- Backend: FastAPI app in `api/` (entry `api/main.py`), SQLite database (no external DB needed), migrations via Alembic. Python deps are managed with `uv` (`pyproject.toml` + `uv.lock`); `uv sync` creates a `.venv` in the repo root. Run backend commands with `uv run ...` (no manual venv activation needed).
- Frontend: Vue 3 + Vite + Tailwind CSS + shadcn-vue SPA in `src/` (dev server on port 5173). See `DESIGN.md` and `SITE_MAP.md` for UI/routing.

Standard commands live in `README.md`, `package.json`, and `pyproject.toml`. Below are only the non-obvious caveats.

## Environment variables (`.env`)

- A `.env` file at the repo root is required for BOTH services and is gitignored, so it is not in version control. It persists in the VM snapshot; recreate it only if missing. Required keys (dev values are fine locally): `VITE_APP_TITLE`, `VITE_API_URL=http://localhost:8000/api`, `VITE_GOOGLE_CLIENT_ID` (any non-empty placeholder), `ENVIRONMENT=development`, `SECRET_KEY`, `SUPERUSER_GID`.
- Non-obvious: Vite's `validateVars` plugin (in `vite.config.ts`) reads `process.env`, NOT the `.env` file. You MUST export the vars into the shell before running `pnpm dev`/`pnpm build`, e.g. `set -a && . ./.env && set +a && pnpm dev`. Running `pnpm dev` without exporting fails with "Required environment variables are missing".
- Non-obvious: the FastAPI settings (`api/core/config.py`) point `env_file` at `../.env` (outside the repo when run from the root), so the backend effectively relies on process env vars. Export `.env` the same way before running the backend: `set -a && . ./.env && set +a && uv run fastapi dev api/main.py`.

## Database setup (not part of the dependency update script)

- The SQLite DB lives at `data/database.db`. Create dirs and run migrations + seed once: `mkdir -p data/uploads data/logs && set -a && . ./.env && set +a && uv run alembic upgrade head && uv run python -m api.scripts.load_data`. The seed creates one admin user (from `SUPERUSER_GID`) and 10 sample recipes. This is state setup, so it is intentionally NOT in the startup update script.

## Running the services

- Backend: `set -a && . ./.env && set +a && uv run fastapi dev api/main.py --host 0.0.0.0 --port 8000` (docs at `/api/docs`).
- Frontend: `set -a && . ./.env && set +a && pnpm dev --host 0.0.0.0 --port 5173`.

## Authentication caveat (testing logged-in flows)

- Login is Google OAuth only (`/auth/login-google/`), so there is no username/password login. To exercise authenticated UI/endpoints without real Google credentials, mint a session token for the seeded admin user using the app's own logic and inject it into browser `localStorage` under key `access_token`:
  ```python
  # run with `uv run python` and .env exported
  from sqlmodel import Session, select
  from api.core.database import engine
  from api.core.authentication import create_access_token
  from api.models import User
  with Session(engine) as s:
      u = s.exec(select(User)).first()
      print(create_access_token({"sub": u.google_user_id, "email": u.email, "name": u.display_name, "picture": None}, s).access_token)
  ```
  Then in the browser console: `localStorage.setItem('access_token','<token>')` and reload. The frontend router redirects unauthenticated users to `/login`.

## Lint / test / build

- Frontend lint: `pnpm lint` (ESLint; note it runs with `--fix`). Build (includes `vue-tsc` type-check): `pnpm build`.
- Python linters `flake8`/`black`/`isort` are in the `dev` dependency group; run them via `uv run flake8 api alembic` / `uv run black api alembic`. They have pre-existing findings in `api/core/seed_database.py` (long seed strings) and the Alembic migrations; these are not from new work.
- There is no automated test suite (no pytest/vitest configured).

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

- The SQLite DB lives at `data/database.db`. Create dirs and run migrations + seed once: `mkdir -p data/uploads data/logs && set -a && . ./.env && set +a && uv run alembic upgrade head && uv run python -m api.scripts.load_data`. The seed creates verified admin + test password users and 10 sample recipes. This is state setup, so it is intentionally NOT in the startup update script.

## Running the services

- Backend: `set -a && . ./.env && set +a && uv run fastapi dev api/main.py --host 0.0.0.0 --port 8000` (docs at `/api/docs`).
- Frontend: `set -a && . ./.env && set +a && pnpm dev --host 0.0.0.0 --port 5173`.

## Authentication

Password auth and Google OAuth are both supported.

### Password flow

- `POST /api/auth/register/` — create email/password user (unverified); response includes `redirect_to` (`/verify-email?email=...`) and sets `Location`. In `ENVIRONMENT=development`, response also includes `dev_otp`.
- `POST /api/auth/verify-email/` — confirm OTP, then mint session JWT.
- `POST /api/auth/resend-verification/` — resend OTP (rate-limited; generic response).
- `POST /api/auth/login/` — email/password. If the account exists but is unverified, the API returns **403** with `detail.redirect_to` / `Location: /verify-email?email=...` so the SPA must follow the server-directed page (and may refresh the OTP).
- `POST /api/auth/login-google/` — unchanged Google ID token exchange; Google users are treated as email-verified (and can link to an existing password account with the same email).

OTP codes are HMAC-hashed at rest, expire after `EMAIL_OTP_EXPIRE_MINUTES` (default 15), and attempt-limited. Without SMTP env vars the backend logs the OTP; configure `SMTP_*` + `EMAILS_FROM_EMAIL` to send real mail.

### Seeded local users

`uv run python -m api.scripts.load_data` creates two verified password users (overridable via env):

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@example.com` | `adminpass123` |
| Test | `test@example.com` | `testpass123` |

The admin seed also receives `SUPERUSER_GID` when set.

### Local Vite auto-login bypass

- In local Vite dev (`pnpm dev`), the SPA **auto-logs in** via `POST /api/auth/dev-login/` as the seeded admin (`admin@example.com`). That endpoint returns 404 unless `ENVIRONMENT=development`. The login page also has “Continue as seeded admin”.
- Ensure the DB is seeded first so those users exist.
- Google One Tap is skipped while `import.meta.env.DEV` is true.

## Meal-plan wizard LLM

- Routes under `/api/meal-plan-wizard/`. Pipeline stages: create session → ideate (SSE) → select → build (SSE) → commit.
- Without `OPENROUTER_API_KEY`, the backend uses a deterministic stub LLM (`api/core/llm/client.py`). Set the key (+ optional `OPENROUTER_MODEL`) later to swap in the real client; tool helpers for user-scoped recipe search live in `api/core/llm/tools.py`.

## Lint / test / build

- Frontend lint: `pnpm lint` (ESLint; note it runs with `--fix`). Build (includes `vue-tsc` type-check): `pnpm build`.
- Python linters `flake8`/`black`/`isort` are in the `dev` dependency group; run them via `uv run flake8 api alembic` / `uv run black api alembic`. They have pre-existing findings in `api/core/seed_database.py` (long seed strings) and the Alembic migrations; these are not from new work.
- There is no automated test suite (no pytest/vitest configured).

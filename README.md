# Junket

Personal recipe box, meal planner, and grocery list. (Formerly RecipeDB — the GitHub repo keeps the old name for now.)

**The iOS app is the primary product** — a native Expo / React Native app in [`mobile/`](./mobile/README.md) with the full experience: recipe library, AI meal-plan wizard, week planner, swipeable grocery list. The FastAPI server (`api/`) and the Vue web app (`src/`) support it: the server is the system of record; the web app is a companion UI that shares the same API and design system.

| Part | Where | Stack | Docs |
|---|---|---|---|
| **iOS app** | `mobile/` | Expo SDK 57, React Native, NativeWind, expo-router | [`mobile/README.md`](./mobile/README.md) |
| API server | `api/` | FastAPI, SQLModel, SQLite, Alembic, uv | this file + [`docs/cursor-cloud-agents.md`](./docs/cursor-cloud-agents.md) |
| Web app | `src/` | Vue 3, Vite, Tailwind CSS v4, shadcn-vue | [`DESIGN.md`](./DESIGN.md), [`SITE_MAP.md`](./SITE_MAP.md) |

## Setup

### Step 1 - Environment

Copy `.envtemplate` to a new file, `.env`, and fill out applicable values.

The backend uses [uv](https://docs.astral.sh/uv/) to manage its Python environment. Install it (see the [uv install docs](https://docs.astral.sh/uv/getting-started/installation/)):

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Step 2 - Install dependencies

```bash
# Web app deps
pnpm i

# iOS app deps
cd mobile && pnpm i && cd ..

# Create the virtual environment (.venv) and install Python deps from uv.lock
uv sync
```

`uv sync` reads `pyproject.toml` / `uv.lock` and creates a `.venv` in the project root. When using VSCode, select `.venv` as your Python interpreter (`Ctrl` + `Shift` + `P` -> `Python: Select Interpreter`).

### Step 3 - Database

```bash
mkdir -p data/uploads data/logs
set -a && . ./.env && set +a
uv run alembic upgrade head
uv run python -m api.scripts.load_data   # seed users + sample recipes
```

## Development

```bash
# Export env vars first (required by both server and web dev builds)
set -a && . ./.env && set +a

# API server (docs at http://localhost:8000/api/docs)
uv run fastapi dev api/main.py

# iOS app — web preview for quick iteration; see mobile/README.md for device builds
cd mobile && pnpm web

# Web app (http://localhost:5173)
pnpm dev
```

Auth supports email/password (with OTP email verification), Google OAuth, and Sign in with Apple (iOS app). Seeded locals after `uv run python -m api.scripts.load_data` (sign in via the normal login form):

- Admin: `admin@example.com` / `adminpass123`
- Test: `test@example.com` / `testpass123`

See `docs/cursor-cloud-agents.md` for the full auth flow.

## Checks

```bash
pnpm lint          # web app eslint (runs with --fix)
pnpm build         # web app type-check + production build

cd mobile
pnpm lint && pnpm typecheck && pnpm test   # iOS app
```

## Deployment

- **Server + web app**: pushes to `main` build a Docker image (web bundle baked in) and deploy it via webhook — `.github/workflows/CI_CD.yaml`.
- **iOS app**: pushes to `main` touching `mobile/` build, sign, and upload to TestFlight from a macOS runner — `.github/workflows/MobileRelease.yaml`. Apple credential setup is documented in [`mobile/README.md`](./mobile/README.md).

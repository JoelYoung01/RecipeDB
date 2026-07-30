# AGENTS.md

## Cursor Cloud specific instructions

Before setting up, running, or testing this project, read [`docs/cursor-cloud-agents.md`](docs/cursor-cloud-agents.md). It documents the services, required `.env` vars and non-obvious env-export gotchas, DB migrate/seed steps, how to run/lint/build each service, and how to test Google-OAuth-only authenticated flows.

## Product structure

The **iOS app (`mobile/`) is the primary product**; the FastAPI server (`api/`) is the system of record and the Vue web app (`src/`) is a companion UI. When changing API contracts, update both clients (`src/types/` for web, `mobile/src/types/` for mobile).

## iOS app (`mobile/`)

- Stack: Expo SDK 57 + React Native + TypeScript, `expo-router` file-system routes, NativeWind (Tailwind classes) with shadcn-style primitives in `mobile/src/components/ui/`. Jest (`jest-expo`) + React Native Testing Library (note: RNTL v14 `render`/`fireEvent` are async — `await` them).
- Design tokens mirror the web app (dark zinc + green, Figtree): `mobile/tailwind.config.js` + `mobile/src/lib/colors.ts`. Follow `DESIGN.md` for look & feel.
- Routes mirror `SITE_MAP.md` via `mobile/src/lib/sitemap.ts`; keep it in sync with `src/sitemap.ts` when routes change.
- The native `ios/` directory is generated (`expo prebuild`), never committed.
- Run checks from `mobile/`: `pnpm lint`, `pnpm typecheck`, `pnpm test`. Iterate on Linux with `pnpm web` (Expo web preview).

## Web frontend design & routing (`src/`)

- Visual system: [`DESIGN.md`](./DESIGN.md) (shadcn-vue, dark zinc + green, mobile shell). Follow it for UI work.
- Site structure: [`SITE_MAP.md`](./SITE_MAP.md) and the mirrored module [`src/sitemap.ts`](./src/sitemap.ts). Add or rename routes in both places; the router and tab bar consume `sitemap.ts`.
- UI stack: Vue 3 + Vite + Tailwind CSS v4 + shadcn-vue (Reka UI). Do not reintroduce Vuetify.

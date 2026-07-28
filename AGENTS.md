# AGENTS.md

## Cursor Cloud specific instructions

Before setting up, running, or testing this project, read [`docs/cursor-cloud-agents.md`](docs/cursor-cloud-agents.md). It documents the two services, required `.env` vars and non-obvious env-export gotchas, DB migrate/seed steps, how to run/lint/build each service, and how to test Google-OAuth-only authenticated flows.

## Frontend design & routing

- Visual system: [`DESIGN.md`](./DESIGN.md) (shadcn-vue, dark zinc + green, mobile shell). Follow it for UI work.
- Site structure: [`SITE_MAP.md`](./SITE_MAP.md) and the mirrored module [`src/sitemap.ts`](./src/sitemap.ts). Add or rename routes in both places; the router and tab bar consume `sitemap.ts`.
- UI stack: Vue 3 + Vite + Tailwind CSS v4 + shadcn-vue (Reka UI). Do not reintroduce Vuetify.

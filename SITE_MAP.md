# Site map

Canonical map of routes, layouts, and page modules. The TypeScript module [`src/sitemap.ts`](./src/sitemap.ts) mirrors this file and is what the router and nav chrome import.

## Auth

| Path | Name | Page | Auth | Notes |
|------|------|------|------|-------|
| `/login` | `login` | `views/LoginView.vue` | Public | Email/password + Google; redirects to `redirectUrl` or home |
| `/register` | `register` | `views/RegisterView.vue` | Public | Create email/password account → server redirects to verify |
| `/verify-email` | `verify-email` | `views/VerifyEmailView.vue` | Public | OTP confirmation; query `?email=` |

Unauthenticated visits to protected routes → `/login?redirectUrl=<fullPath>`.

Unverified password login → API `403` with `Location` / `redirect_to` → `/verify-email?email=...`.

## App shell (bottom tab bar)

Layout: `layouts/AppShell.vue` (tab bar + add sheet). Children render in the shell outlet.

| Path | Name | Page | Tab | Notes |
|------|------|------|-----|-------|
| `/` | — | — | — | Redirect → `/home` |
| `/home` | `home` | `views/HomeView.vue` | Home | Tonight hero, week strip, action rows |
| `/recipes` | `recipes` | `views/recipes/RecipesView.vue` | Recipes | User’s recipes + search |
| `/planner` | `planner` | `views/planner/PlannerView.vue` | Planner | Calendar meal planning |
| `/list` | `list` | `views/list/ShoppingListView.vue` | List | UI shell only (no shopping-list API yet) |
| `/account` | `account` | `views/AccountView.vue` | — | Profile; opened from home avatar |

### Add menu (sheet, not a tab destination)

Opened by the raised **+** control. Items:

| Action | Target | Status |
|--------|--------|--------|
| Import from link | `/recipes/import?method=link` | UI stub (no import API) |
| Scan a photo | `/recipes/import?method=photo` | UI stub |
| Write from scratch | `/recipes/new` | Live |
| Add meal to plan | `/planner` | Live |
| Add to shopping list | `/list` | UI shell |

## Recipe flows (no tab highlight, or Recipes)

| Path | Name | Page | Auth | Notes |
|------|------|------|------|-------|
| `/recipes/new` | `recipe-new` | `views/recipes/RecipeEditView.vue` | Required | Create |
| `/recipes/import` | `recipe-import` | `views/recipes/RecipeImportView.vue` | Required | Stub UI for link/photo import |
| `/recipes/:recipeId` | `recipe-detail` | `views/recipes/RecipeDetailView.vue` | Required | `:recipeId` = `\d+` |
| `/recipes/:recipeId/edit` | `recipe-edit` | `views/recipes/RecipeEditView.vue` | Required | Edit owned recipe |

## Social / misc

| Path | Name | Page | Auth | Notes |
|------|------|------|------|-------|
| `/users/:userId` | `public-user` | `views/PublicUserView.vue` | Required | Public profile + recipes |
| `/:pathMatch(.*)*` | `not-found` | `views/NotFoundView.vue` | Required | 404 |

## Legacy path redirects

Preserve bookmarks from the Vuetify app:

| Old | New |
|-----|-----|
| `/discover` | `/recipes` |
| `/my-recipes` | `/recipes` |
| `/meal-planning` | `/planner` |
| `/add-recipe` | `/recipes/new` |
| `/my-account` | `/account` |
| `/recipe/:id/detail` | `/recipes/:id` |
| `/recipe/:id/edit` | `/recipes/:id/edit` |
| `/user/:id` | `/users/:id` |

## Feature coverage (no new product scope)

- **Recipe storage** — list, search, detail, create/edit, delete, cover image, public flag
- **Meal planning** — plan/unplan by day; home week strip + tonight hero
- **Import recipe** — entry points in UI; link/photo remain stubs until a backend exists
- **Shopping list** — nav + empty shell only (design surface; no persistence yet)

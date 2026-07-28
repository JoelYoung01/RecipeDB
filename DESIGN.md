# Design system

Source of truth for visual language. Derived from the Recipe App Home design exploration (hero-driven home + raised “+” sheet). Implement UI against this doc and [`SITE_MAP.md`](./SITE_MAP.md).

## Product feel

- Mobile-first web app (PWA-style). Primary canvas ≈ 390px wide, centered on larger screens (`max-w-md`).
- Users come to: (a) import a recipe, (b) find a saved recipe, (c) plan meals, (d) see what’s for dinner tonight.
- Dark only for now — no light theme.

## Typography

- **UI font:** Figtree (Google Fonts), weights 400–700.
- Avoid Inter / Roboto / Arial / system stacks as the primary face.
- Hierarchy (home as reference):
  - Weekday header: 16px / 700
  - Hero recipe title: 20px / 700
  - Section / row labels: 14–14.5px / 600
  - Meta / muted: 11–12.5px / 400–600
  - Tab labels: 10px / 500–600
  - Eyebrow (“TONIGHT”): 11px / 700 / letter-spacing ~0.08em / uppercase

## Color (zinc dark + green accent)

| Token | Hex | Usage |
|-------|-----|--------|
| `--background` | `#09090b` | App canvas |
| `--card` | `#18181b` | Rows, sheets, surfaces |
| `--elevated` | `#111113` / `#1f1f23` | Tab bar / highlighted sheet rows |
| `--border` | `#27272a` | Hairlines, card borders |
| `--foreground` | `#fafafa` | Primary text |
| `--muted-foreground` | `#a1a1aa` | Secondary text |
| `--faint` | `#6b6b74` | Tertiary / placeholders |
| `--gap-dot` | `#3f3f46` | Unplanned day indicator |
| Primary fill | `#16a34a` (`green-600`) | Buttons, FAB |
| Primary on-dark | `#22c55e` (`green-500`) | Icons, links, active tab |
| Success soft | `#4ade80` / `#86efac` | Badges, “TONIGHT” eyebrow |
| Tints | `rgba(34,197,94,…)` | Today cell, badge chips |

Map these to shadcn CSS variables (`--primary`, `--background`, etc.) in `src/assets/index.css`. Keep **dark class** on `<html>`.

## Shape & elevation

- Radius: ~12–14px for rows/cards; ~20px top radius on bottom sheets; FAB fully round.
- Borders: 1px `#27272a`. Prefer border + flat fill over heavy shadows.
- FAB shadow: `0 4px 12px rgba(22,163,74,.4)` with 4px canvas-colored ring.

## Layout patterns

### App chrome

1. **Scrollable content** above a fixed bottom tab bar.
2. **Tab bar** (global): Home · Recipes · **[+]** · Planner · Grocery.
3. Raised center **+** opens the Add sheet (not a direct route). When open, “+” rotates to × / “Close”.
4. Safe-area padding under the tab bar (~20px) for home-indicator devices.

### Home (landed direction)

Column: **full-bleed Tonight hero** → **week-at-a-glance** → **action rows** → tab bar.

- Hero (~300px): recipe photo, gradient scrim, weekday + profile avatar overlay, “TONIGHT” + title + meta + **Cook** CTA. Empty state: prompt to plan tonight.
- Week strip: swipeable weeks (past + future) with weekday + date; green dot = planned, zinc gap = unplanned; today tinted/outlined. Tap a day → that day’s plan in the planner. “Fill the gaps →” → planner fill wizard for the visible week.
- Planner: vertical sliding weeks with **this week sticky at top**; day rows (not a month grid). “Plan week” / “Fill gaps” open the wizard.
- Action rows (not a recent-feed): Import a recipe · Find a recipe · Grocery (7-day chip / count when available).

### Add sheet

Bottom sheet over dimmed scrim:

1. **Add new** — Import from link (highlighted), Scan a photo, Write from scratch.
2. Divider
3. **Quick adds** — Add meal to plan, Grocery list.

Wire only to existing features; stub unavailable import flows in UI without inventing backend behavior.

## Motion

Keep motion intentional and light (app-wide):

1. Sheet slide-up + scrim fade.
2. FAB “+” → “×” rotate.
3. Subtle press/active opacity on action rows and tab items.
4. Page transitions: short fade + slight vertical rise (~180ms) between shell routes.
5. Skeleton pulse (`animate-pulse` muted bars) while list/hero data loads — never blank the page behind “Loading…”.

## Loading & caching

- Tab roots (Home, Recipes, Planner, Grocery) stay mounted via `KeepAlive` after first visit.
- Shared Pinia stores (`recipes`, `planner`, `grocery`) hold fetched data so revisits paint immediately; soft-refresh in the background when needed.
- First paint shows page chrome + skeletons; content fills in when the network returns.
- Prefer slim list DTOs (`RecipeCard`) and summary/count endpoints for badges over shipping full payloads.

## Components (shadcn-vue)

Prefer primitives from `@/components/ui/*`: Button, Input, Textarea, Checkbox, Dialog, Sheet, Calendar, Popover, Separator, Badge, Avatar, Label, ScrollArea, Skeleton, etc.

App-specific compositions live under `@/components/` (e.g. `AppTabBar`, `AddMenuSheet`, `RecipeCard`, `TonightHero`).

## Imagery

- Recipe covers are the visual anchor. Use real cover URLs from the API; fall back to `@/assets/default-recipe.jpg`.
- Dev: prefix relative upload URLs with `http://localhost:8000`.

## Anti-patterns

- No Vuetify / MDI.
- No purple-gradient “AI default” look; no cream/serif terracotta kit; no broadsheet newspaper layout.
- No card grids in the hero; no floating promo badges on hero media.
- Don’t put brand wordmark on home — weekday is the header; brand lives on login / account.

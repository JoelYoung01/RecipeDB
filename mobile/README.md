# RecipeDB iOS app

Native iOS app for RecipeDB, built with [Expo](https://expo.dev) / React Native. It mirrors the web UI feature-for-feature — same dark zinc + green design system, same API — with native navigation, gestures, haptics, and secure keychain sessions.

## Stack

| Concern | Choice |
|---|---|
| Framework | React Native 0.86 + Expo SDK 57 (TypeScript) |
| Navigation | `expo-router` (file-system routes, typed) |
| Styling | NativeWind 4 (Tailwind CSS classes, shadcn-style components in `src/components/ui/`) |
| Server state | `@tanstack/react-query` |
| Local state | `zustand` (session, toasts) |
| Auth storage | `expo-secure-store` (iOS Keychain) |
| Fonts / icons | Figtree (`@expo-google-fonts`) / `lucide-react-native` |
| Tests | Jest (`jest-expo`) + React Native Testing Library |

The native `ios/` project is **generated, never committed** (Expo [Continuous Native Generation](https://docs.expo.dev/workflow/continuous-native-generation/)): `pnpm exec expo prebuild -p ios` recreates it from `app.config.ts` at any time.

## Development

All commands run from `mobile/`.

```bash
pnpm install

# iterate on Linux/Windows/macOS — web preview at http://localhost:8081
pnpm web

# on a Mac with Xcode — build & run the iOS simulator
pnpm ios

# on your iPhone without a Mac — install the Expo Go app, then
pnpm start   # scan the QR code from Expo Go
```

The app talks to the FastAPI backend. For local development start it from the repo root (see the root README), and the app's default `http://localhost:8000/api` will reach it. Point a device/simulator elsewhere with an env var:

```bash
EXPO_PUBLIC_API_URL="https://recipe-db.example.dev/api" pnpm web
```

### Quality gates

```bash
pnpm lint        # eslint (expo config)
pnpm typecheck   # tsc --noEmit
pnpm test        # jest unit + component tests
```

CI runs all three plus `expo prebuild` / `expo export` sanity checks on every PR that touches `mobile/` (`.github/workflows/MobileCI.yaml`).

## Configuration

`EXPO_PUBLIC_*` vars are inlined into the JS bundle at build time (see `src/config.ts`):

| Variable | Purpose | Default |
|---|---|---|
| `EXPO_PUBLIC_API_URL` | API base URL | `http://localhost:8000/api` in dev, production URL in release |
| `EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID` | iOS OAuth client for native Google sign-in | empty → Google button hidden |
| `EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID` | Web OAuth client (used by the web preview) | empty |

Native project settings (bundle id, build number) come from env vars read in `app.config.ts`: `RECIPEDB_IOS_BUNDLE_ID`, `RECIPEDB_IOS_BUILD_NUMBER`.

## Releasing to your phone (TestFlight)

`.github/workflows/MobileRelease.yaml` builds, signs, and uploads the app to TestFlight on every push to `main` that touches `mobile/`. Signing uses Xcode **cloud-managed signing** with an App Store Connect API key — no certificates or provisioning profiles to export and rotate by hand.

Until the secrets below exist, the workflow skips the signed build with a warning (it stays green).

### One-time Apple setup

1. Join the [Apple Developer Program](https://developer.apple.com/programs/) ($99/year) with your Apple ID.
2. In [App Store Connect → Users and Access → Integrations → App Store Connect API](https://appstoreconnect.apple.com/access/integrations/api), create a **Team key** with the **App Manager** role. Note the **Key ID** and **Issuer ID**, and download the `.p8` file (only downloadable once).
3. In [App Store Connect → Apps](https://appstoreconnect.apple.com/apps), click **+ → New App**: platform iOS, any name (e.g. RecipeDB), bundle ID `com.joelyoung.recipedb` (register it on the same page if prompted; must match `RECIPEDB_IOS_BUNDLE_ID` if you override it), SKU anything (e.g. `recipedb`).
4. Find your **Team ID** in [Apple Developer → Membership](https://developer.apple.com/account#MembershipDetailsCard) (10-character string).

### GitHub repository secrets

| Secret | Value |
|---|---|
| `APPLE_TEAM_ID` | 10-char Team ID |
| `ASC_KEY_ID` | API key's Key ID |
| `ASC_ISSUER_ID` | API key's Issuer ID |
| `ASC_PRIVATE_KEY` | Full contents of the `.p8` file (multiline is fine) |
| `GOOGLE_IOS_CLIENT_ID` | Optional — iOS OAuth client id for Google sign-in |

Also uses existing repo config: `vars.API_URL` (JS bundle API base) and `secrets.GOOGLE_CLIENT_ID` (web OAuth client). Optional `vars.RECIPEDB_IOS_BUNDLE_ID` overrides the bundle id.

### Installing on your phone

1. Install **TestFlight** from the App Store and sign in with the same Apple ID.
2. After the first successful workflow run, the build appears in App Store Connect → TestFlight (a few minutes of processing). Add yourself as an internal tester on the same page.
3. Open TestFlight on the phone → install RecipeDB. Subsequent merges to `main` push new builds automatically and TestFlight notifies you.

Each run also attaches the raw `.ipa` as a workflow artifact for ad-hoc installs.

### Google sign-in on iOS (optional)

Password login works out of the box. For the Google button:

1. In [Google Cloud Console → Credentials](https://console.cloud.google.com/apis/credentials), create an **OAuth client ID** of type **iOS** with bundle ID `com.joelyoung.recipedb`.
2. Set the client id as the `GOOGLE_IOS_CLIENT_ID` GitHub secret (baked into the app) **and** in the server's `.env` (`GOOGLE_IOS_CLIENT_ID=...`) so the API accepts tokens minted for the iOS client.

## Project layout

```
mobile/
├── app.config.ts          # Expo config (bundle id, splash, plugins)
├── src/
│   ├── app/               # expo-router routes
│   │   ├── (auth)/        # login, register, verify-email
│   │   └── (app)/         # authed area
│   │       ├── (tabs)/    # home, recipes, planner, list (grocery)
│   │       ├── recipes/   # detail, new, edit, import
│   │       ├── planner/   # fill (meal-plan wizard)
│   │       └── account.tsx
│   ├── api/               # fetch client, SSE, per-resource API modules
│   ├── components/        # screens' building blocks + ui/ primitives
│   ├── hooks/             # react-query hooks per resource
│   ├── stores/            # zustand: session (SecureStore), toasts
│   ├── lib/               # dates, colors, media, haptics, sitemap
│   └── types/             # API contracts (mirrors api/schemas.py)
├── assets/                # icon, splash, fonts, images
└── test/                  # jest setup
```

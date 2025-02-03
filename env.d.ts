/// <reference types="vite/client" />
/// <reference types="google.accounts" />

interface ImportMetaEnv {
  readonly VITE_APP_TITLE: string;
  readonly VITE_API_URL: string;
  readonly VITE_GOOGLE_CLIENT_ID: string;
  // Add Env Variables here
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

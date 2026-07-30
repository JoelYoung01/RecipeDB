/**
 * Dev-only OTP stash. When the API runs without SMTP configured it returns
 * `dev_otp` in auth responses; we keep it in memory so the verify screen can
 * show it (mirrors the web app's sessionStorage behavior).
 */
const stash = new Map<string, string>();

export function stashDevOtp(email: string, otp: string) {
  stash.set(email.toLowerCase(), otp);
}

export function readDevOtp(email: string): string | null {
  return stash.get(email.toLowerCase()) ?? null;
}

export function clearDevOtp(email: string) {
  stash.delete(email.toLowerCase());
}

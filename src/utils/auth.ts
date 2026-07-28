export const AuthLoginEvent = "auth:login";

export async function checkSessionToken(access_token: string) {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/verify-session/`, {
      headers: {
        Authorization: `Bearer ${access_token}`
      }
    });
    if (!response.ok) throw new Error("Recieved Non-200 response code while verifying session");
    return await response.json();
  } catch (er) {
    console.error(er);
  }
}

function dispatchLogin(access_token: string, user: unknown) {
  window.dispatchEvent(new CustomEvent(AuthLoginEvent, { detail: { access_token, user } }));
}

export async function loginWithGoogle(payload: any) {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/login-google/`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error(`Error logging in with google: ${response.statusText}`);
    const { access_token, user } = await response.json();

    dispatchLogin(access_token, user);
  } catch (er) {
    console.error(er);
  }
}

/** Development-only: session for the seeded test/admin user (no Google). */
export async function loginAsDevUser() {
  try {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/dev-login/`, {
      method: "POST",
      headers: { "content-type": "application/json" }
    });
    if (!response.ok) {
      throw new Error(`Dev login failed: ${response.status} ${response.statusText}`);
    }
    const { access_token, user } = await response.json();
    dispatchLogin(access_token, user);
    return { access_token, user };
  } catch (er) {
    console.error(er);
  }
}

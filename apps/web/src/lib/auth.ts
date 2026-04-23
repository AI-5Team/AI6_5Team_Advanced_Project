import type { AuthUser } from "@/lib/contracts";

const AUTH_STORAGE_KEY = "studio-auth-session";

export interface AuthSession {
  user: AuthUser;
}

function isBrowser() {
  return typeof window !== "undefined";
}

export function getStoredAuthSession(): AuthSession | null {
  if (!isBrowser()) return null;
  const raw = window.localStorage.getItem(AUTH_STORAGE_KEY);
  if (!raw) return null;
  try {
    const parsed = JSON.parse(raw) as Partial<AuthSession>;
    if (!parsed.user || typeof parsed.user.id !== "string") {
      return null;
    }
    return { user: parsed.user };
  } catch {
    return null;
  }
}

export function setStoredAuthSession(session: AuthSession) {
  if (!isBrowser()) return;
  window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session));
}

export function clearStoredAuthSession() {
  if (!isBrowser()) return;
  window.localStorage.removeItem(AUTH_STORAGE_KEY);
}

// Cookie-based auth — no Authorization header needed
export function buildAuthHeaders(): Record<string, string> {
  return {};
}

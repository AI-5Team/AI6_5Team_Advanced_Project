import type { AuthUser } from "@/lib/contracts";

// 레거시 localStorage 세션 — Bearer 토큰 방식 지원 유지 (기존 호환성)
const AUTH_STORAGE_KEY = "studio-auth-session";

export interface AuthSession {
  accessToken: string;
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
    if (
      typeof parsed.accessToken !== "string" ||
      !parsed.accessToken ||
      !parsed.user ||
      typeof parsed.user.id !== "string"
    ) {
      return null;
    }
    return { accessToken: parsed.accessToken, user: parsed.user };
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

export function buildAuthHeaders(): Record<string, string> {
  const session = getStoredAuthSession();
  if (!session) return {};
  return { Authorization: `Bearer ${session.accessToken}` };
}

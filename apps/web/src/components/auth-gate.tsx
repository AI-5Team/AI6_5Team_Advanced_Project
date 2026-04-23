"use client";

import type { FormEvent, ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Link from "next/link";

import { AppNav } from "@/components/app-nav";
import { clearStoredAuthSession, setStoredAuthSession } from "@/lib/auth";
import { getMe, loginUser, logoutUser } from "@/lib/api";
import type { AuthUser, LoginRequest } from "@/lib/contracts";

const DEMO_LOGIN = {
  email: "demo-owner@example.com",
  password: "secret123!",
} as const;

export function AuthGate({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [initializing, setInitializing] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [feedback, setFeedback] = useState("");
  const [loginForm, setLoginForm] = useState<LoginRequest>({ ...DEMO_LOGIN });

  const isSceneFrame = pathname?.startsWith("/scene-frame") ?? false;
  const PUBLIC_PATHS = ["/login", "/register", "/logout", "/terms", "/privacy", "/email-verify", "/password-reset"];
  const isPublicPath = PUBLIC_PATHS.some((p) => pathname === p || (pathname?.startsWith(p + "/") ?? false));
  const summaryText = useMemo(() => {
    if (!user) return "";
    return `${user.name} · ${user.email}`;
  }, [user]);

  useEffect(() => {
    let cancelled = false;

    async function bootstrap() {
      try {
        const me = await getMe();
        if (cancelled) return;
        setUser(me);
        setStoredAuthSession({ user: me });
        setFeedback("인증이 확인되어 trunk 기준 화면을 바로 이어서 엽니다.");
      } catch {
        clearStoredAuthSession();
      } finally {
        if (!cancelled) setInitializing(false);
      }
    }

    void bootstrap();

    return () => {
      cancelled = true;
    };
  }, []);

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSubmitting(true);
    setFeedback("로그인 정보를 확인하고 있습니다.");
    try {
      const response = await loginUser(loginForm);
      setStoredAuthSession({ user: response.user });
      setUser(response.user);
      setFeedback("로그인이 완료되었습니다. 현재 작업 화면으로 이어집니다.");
      router.refresh();
    } catch (error) {
      setFeedback(
        error instanceof Error ? error.message : "로그인에 실패했습니다.",
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleLogout = async () => {
    setSubmitting(true);
    try {
      await logoutUser().catch(() => undefined);
      clearStoredAuthSession();
      setUser(null);
      setFeedback("로그아웃되었습니다.");
      router.refresh();
    } finally {
      setSubmitting(false);
    }
  };

  const handleUseDemo = () => {
    setLoginForm({ ...DEMO_LOGIN });
    setFeedback("데모 계정으로 바로 확인할 수 있습니다.");
  };

  if (initializing) {
    if (isPublicPath) return <>{children}</>;
    return (
      <main className="auth-screen">
        <section className="auth-panel auth-panel--loading">
          <strong>세션을 확인하고 있습니다.</strong>
          <p>기존 작업 기준선과 인증 상태를 함께 불러옵니다.</p>
        </section>
      </main>
    );
  }

  if (!user) {
    if (isPublicPath) return <>{children}</>;
    return (
      <main className="auth-screen">
        <section className="auth-panel">
          <div className="auth-panel__visual">
            <img src="/sample-assets/beer.jpg" alt="" />
            <div className="auth-panel__shade" />
            <div className="auth-panel__copy">
              <span>Root Trunk</span>
              <h1>한 기준선에서 다시 이어갑니다.</h1>
              <p>로그인 후 만들기, 이력, 채널 화면을 같은 계약과 같은 trunk에서 확인합니다.</p>
              <div className="auth-panel__meta">
                <span>API 계약 유지</span>
                <span>Next.js 화면 유지</span>
                <span>worker adapter 경계 유지</span>
              </div>
            </div>
          </div>

          <div className="auth-panel__form">
            <div className="auth-copy">
              <strong>기존 계정으로 시작</strong>
              <p>{feedback || "로그인 후 현재 trunk 기준 화면을 그대로 이어서 사용합니다."}</p>
            </div>

            <form className="auth-form" onSubmit={handleLogin}>
              <label className="auth-field">
                <span>이메일</span>
                <input
                  type="email"
                  value={loginForm.email}
                  onChange={(event) =>
                    setLoginForm((current) => ({ ...current, email: event.target.value }))
                  }
                  autoComplete="email"
                  required
                />
              </label>
              <label className="auth-field">
                <span>비밀번호</span>
                <input
                  type="password"
                  value={loginForm.password}
                  onChange={(event) =>
                    setLoginForm((current) => ({ ...current, password: event.target.value }))
                  }
                  autoComplete="current-password"
                  required
                />
              </label>
              <div className="auth-actions">
                <button type="submit" className="button button-primary" disabled={submitting}>
                  {submitting ? "확인 중" : "로그인"}
                </button>
                <button type="button" className="button button-secondary" onClick={handleUseDemo}>
                  데모 계정 채우기
                </button>
              </div>
            </form>

            <div className="auth-links">
              <Link href="/register">계정이 없으신가요? 회원가입 →</Link>
            </div>

            <div className="auth-helper">
              <strong>데모 계정</strong>
              <span>{DEMO_LOGIN.email}</span>
              <span>{DEMO_LOGIN.password}</span>
            </div>
          </div>
        </section>
      </main>
    );
  }

  return (
    <>
      <AppNav />
      {!isSceneFrame ? (
        <section className="auth-status-bar-wrap">
          <div className="auth-status-bar">
            <div className="auth-status-bar__copy">
              <strong>로그인됨</strong>
              <span>{summaryText}</span>
            </div>
            <div className="auth-status-bar__actions">
              <button type="button" className="button button-ghost" onClick={handleLogout} disabled={submitting}>
                로그아웃
              </button>
            </div>
          </div>
        </section>
      ) : null}
      {children}
    </>
  );
}

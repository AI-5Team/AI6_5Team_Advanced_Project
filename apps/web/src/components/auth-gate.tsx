"use client";

import type { FormEvent, ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";
import { usePathname, useRouter } from "next/navigation";

import { AppNav } from "@/components/app-nav";
import { clearStoredAuthSession, getStoredAuthSession, setStoredAuthSession } from "@/lib/auth";
import { getMe, loginUser, logoutUser, registerUser } from "@/lib/api";
import type { AuthUser, LoginRequest, RegisterRequest } from "@/lib/contracts";

type AuthMode = "login" | "register";

const DEMO_LOGIN = {
  email: "demo-owner@example.com",
  password: "secret123!",
} as const;

const INITIAL_REGISTER_FORM: RegisterRequest = {
  name: "",
  email: "",
  password: "",
};

export function AuthGate({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [mode, setMode] = useState<AuthMode>("login");
  const [initializing, setInitializing] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [feedback, setFeedback] = useState("로그인 후 현재 trunk 기준 화면을 그대로 이어서 사용합니다.");
  const [loginForm, setLoginForm] = useState<LoginRequest>({ ...DEMO_LOGIN });
  const [registerForm, setRegisterForm] = useState<RegisterRequest>(INITIAL_REGISTER_FORM);
  const [agreedToTerms, setAgreedToTerms] = useState(false);

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
      const session = getStoredAuthSession();
      if (!session) {
        if (!cancelled) setInitializing(false);
        return;
      }

      try {
        const me = await getMe();
        if (cancelled) return;
        setUser(me);
        setStoredAuthSession({ accessToken: session.accessToken, user: me });
        setFeedback("인증이 확인되어 trunk 기준 화면을 바로 이어서 엽니다.");
      } catch (error) {
        clearStoredAuthSession();
        if (cancelled) return;
        setFeedback(
          error instanceof Error ? error.message : "세션을 다시 확인해 주세요.",
        );
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
      setStoredAuthSession(response);
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

  const handleRegister = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!agreedToTerms) {
      setFeedback("이용약관과 개인정보처리방침에 동의해야 합니다.");
      return;
    }
    setSubmitting(true);
    setFeedback("계정을 만들고 있습니다.");
    try {
      const response = await registerUser(registerForm);
      setStoredAuthSession(response);
      setUser(response.user);
      setRegisterForm(INITIAL_REGISTER_FORM);
      setFeedback("회원가입과 로그인까지 완료되었습니다.");
      router.refresh();
    } catch (error) {
      setFeedback(
        error instanceof Error ? error.message : "회원가입에 실패했습니다.",
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
      setMode("login");
      setFeedback("로그아웃되었습니다.");
      router.refresh();
    } finally {
      setSubmitting(false);
    }
  };

  const handleUseDemo = () => {
    setMode("login");
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
            <div className="auth-toggle" role="tablist" aria-label="인증 화면 전환">
              <button
                type="button"
                className={mode === "login" ? "auth-toggle__button auth-toggle__button--active" : "auth-toggle__button"}
                onClick={() => { setMode("login"); setAgreedToTerms(false); }}
              >
                로그인
              </button>
              <button
                type="button"
                className={mode === "register" ? "auth-toggle__button auth-toggle__button--active" : "auth-toggle__button"}
                onClick={() => setMode("register")}
              >
                회원가입
              </button>
            </div>

            <div className="auth-copy">
              <strong>{mode === "login" ? "기존 계정으로 시작" : "발표 기준 계정 만들기"}</strong>
              <p>{feedback}</p>
            </div>

            {mode === "login" ? (
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
            ) : (
              <form className="auth-form" onSubmit={handleRegister}>
                <label className="auth-field">
                  <span>이름</span>
                  <input
                    type="text"
                    value={registerForm.name}
                    onChange={(event) =>
                      setRegisterForm((current) => ({ ...current, name: event.target.value }))
                    }
                    autoComplete="name"
                    required
                  />
                </label>
                <label className="auth-field">
                  <span>이메일</span>
                  <input
                    type="email"
                    value={registerForm.email}
                    onChange={(event) =>
                      setRegisterForm((current) => ({ ...current, email: event.target.value }))
                    }
                    autoComplete="email"
                    required
                  />
                </label>
                <label className="auth-field">
                  <span>비밀번호</span>
                  <input
                    type="password"
                    value={registerForm.password}
                    onChange={(event) =>
                      setRegisterForm((current) => ({ ...current, password: event.target.value }))
                    }
                    autoComplete="new-password"
                    minLength={8}
                    required
                  />
                </label>
                <label className="auth-field auth-field--checkbox">
                  <input
                    type="checkbox"
                    checked={agreedToTerms}
                    onChange={(e) => setAgreedToTerms(e.target.checked)}
                  />
                  <span>
                    <a href="/terms" target="_blank" rel="noopener noreferrer">이용약관</a>
                    {" "}및{" "}
                    <a href="/privacy" target="_blank" rel="noopener noreferrer">개인정보처리방침</a>
                    에 동의합니다 [필수]
                  </span>
                </label>
                <div className="auth-actions">
                  <button type="submit" className="button button-primary" disabled={submitting || !agreedToTerms}>
                    {submitting ? "등록 중" : "회원가입"}
                  </button>
                  <button type="button" className="button button-secondary" onClick={() => { setMode("login"); setAgreedToTerms(false); }}>
                    로그인으로 돌아가기
                  </button>
                </div>
              </form>
            )}

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

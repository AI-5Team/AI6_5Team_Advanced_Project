"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { loginUser } from "@/lib/api";
import { setStoredAuthSession } from "@/lib/auth";

const DEMO = { email: "demo-owner@example.com", password: "secret123!" };

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const nextPath = searchParams.get("next") ?? "/";

  const [email, setEmail] = useState(DEMO.email);
  const [password, setPassword] = useState(DEMO.password);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setFeedback("");
    try {
      const res = await loginUser({ email, password });
      setStoredAuthSession(res);
      router.replace(nextPath);
    } catch (err) {
      setFeedback(err instanceof Error ? err.message : "로그인에 실패했습니다.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="auth-screen">
      <section className="auth-panel">
        <div className="auth-panel__visual">
          <img src="/sample-assets/beer.jpg" alt="" />
          <div className="auth-panel__shade" />
          <div className="auth-panel__copy">
            <span>가게 숏폼 만들기</span>
            <h1>SNS 콘텐츠를 빠르게 만들어 드립니다.</h1>
            <p>로그인 후 숏폼 영상과 게시글을 바로 시작하세요.</p>
          </div>
        </div>

        <div className="auth-panel__form">
          <div className="auth-copy">
            <strong>로그인</strong>
            {feedback && <p className="auth-feedback auth-feedback--error">{feedback}</p>}
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <label className="auth-field">
              <span>이메일</span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                required
              />
            </label>
            <label className="auth-field">
              <span>비밀번호</span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
              />
            </label>
            <div className="auth-actions">
              <button type="submit" className="button button-primary" disabled={submitting}>
                {submitting ? "확인 중" : "로그인"}
              </button>
            </div>
          </form>

          <div className="auth-links">
            <Link href="/password-reset">비밀번호를 잊으셨나요?</Link>
            <span>·</span>
            <Link href="/register">회원가입</Link>
          </div>

          <div className="auth-helper">
            <strong>데모 계정</strong>
            <span>{DEMO.email}</span>
            <span>{DEMO.password}</span>
          </div>
        </div>
      </section>
    </main>
  );
}

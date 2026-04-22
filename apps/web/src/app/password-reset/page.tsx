"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ?? "";

async function requestReset(email: string) {
  const res = await fetch(`${API_BASE}/api/auth/password/reset-request`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email }),
  });
  if (!res.ok) {
    const data = (await res.json().catch(() => null)) as { error?: { message?: string } } | null;
    throw new Error(data?.error?.message ?? "요청에 실패했습니다.");
  }
  return res.json() as Promise<{ message: string; devToken?: string }>;
}

export default function PasswordResetPage() {
  const [email, setEmail] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const [devToken, setDevToken] = useState("");
  const [feedback, setFeedback] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setFeedback("");
    try {
      const res = await requestReset(email);
      setDone(true);
      if (res.devToken) setDevToken(res.devToken);
    } catch (err) {
      setFeedback(err instanceof Error ? err.message : "요청에 실패했습니다.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="auth-screen">
      <section className="auth-panel auth-panel--slim">
        <div className="auth-copy">
          <strong>비밀번호 재설정</strong>
          {!done && <p>가입한 이메일 주소를 입력하면 재설정 링크를 보내 드립니다.</p>}
        </div>

        {done ? (
          <div className="auth-copy">
            <p>이메일을 확인해 주세요. 링크를 클릭하면 비밀번호를 재설정할 수 있습니다.</p>
            {devToken && (
              <p style={{ fontSize: "0.8rem", color: "var(--muted)" }}>
                [개발용] 토큰: <code>{devToken}</code>
                <br />
                <Link href={`/password-reset/confirm?token=${devToken}`}>바로 이동</Link>
              </p>
            )}
            <Link href="/login" className="button button-secondary" style={{ marginTop: 16 }}>
              로그인으로 돌아가기
            </Link>
          </div>
        ) : (
          <form className="auth-form" onSubmit={handleSubmit}>
            {feedback && <p className="auth-feedback auth-feedback--error">{feedback}</p>}
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
            <div className="auth-actions">
              <button type="submit" className="button button-primary" disabled={submitting}>
                {submitting ? "처리 중" : "재설정 링크 받기"}
              </button>
              <Link href="/login" className="button button-secondary">
                취소
              </Link>
            </div>
          </form>
        )}
      </section>
    </main>
  );
}

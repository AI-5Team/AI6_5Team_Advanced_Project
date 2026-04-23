"use client";

import type { FormEvent } from "react";
import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ?? "";

async function confirmReset(token: string, newPassword: string) {
  const res = await fetch(`${API_BASE}/api/auth/password/reset-confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ token, newPassword }),
  });
  if (!res.ok) {
    const data = (await res.json().catch(() => null)) as { error?: { message?: string } } | null;
    throw new Error(data?.error?.message ?? "재설정에 실패했습니다.");
  }
  return res.json();
}

function PasswordResetConfirmContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";

  const [newPassword, setNewPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState("");

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirm) {
      setFeedback("비밀번호가 일치하지 않습니다.");
      return;
    }
    if (newPassword.length < 10) {
      setFeedback("비밀번호는 10자 이상이어야 합니다.");
      return;
    }
    setSubmitting(true);
    setFeedback("");
    try {
      await confirmReset(token, newPassword);
      router.replace("/login?reset=done");
    } catch (err) {
      setFeedback(err instanceof Error ? err.message : "재설정에 실패했습니다.");
    } finally {
      setSubmitting(false);
    }
  };

  if (!token) {
    return (
      <main className="auth-screen">
        <section className="auth-panel auth-panel--loading">
          <strong>유효하지 않은 링크입니다.</strong>
          <Link href="/password-reset">다시 요청하기</Link>
        </section>
      </main>
    );
  }

  return (
    <main className="auth-screen">
      <section className="auth-panel auth-panel--slim">
        <div className="auth-copy">
          <strong>새 비밀번호 설정</strong>
          {feedback && <p className="auth-feedback auth-feedback--error">{feedback}</p>}
        </div>
        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-field">
            <span>새 비밀번호 (10자 이상)</span>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              autoComplete="new-password"
              minLength={10}
              required
            />
          </label>
          <label className="auth-field">
            <span>비밀번호 확인</span>
            <input
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              autoComplete="new-password"
              required
            />
          </label>
          <div className="auth-actions">
            <button type="submit" className="button button-primary" disabled={submitting}>
              {submitting ? "처리 중" : "비밀번호 변경"}
            </button>
          </div>
        </form>
      </section>
    </main>
  );
}

export default function PasswordResetConfirmPage() {
  return (
    <Suspense
      fallback={(
        <main className="auth-screen">
          <section className="auth-panel auth-panel--loading">
            <strong>비밀번호 재설정 화면을 준비 중입니다...</strong>
          </section>
        </main>
      )}
    >
      <PasswordResetConfirmContent />
    </Suspense>
  );
}

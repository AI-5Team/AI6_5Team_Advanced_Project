"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { setStoredAuthSession } from "@/lib/auth";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ?? "";

async function registerUser(payload: {
  email: string;
  password: string;
  name: string;
  birthDate: string;
  agreedToTerms: true;
  agreedToPrivacy: true;
  agreedToAge14: true;
  agreedToOverseasTransfer: true;
}) {
  const res = await fetch(`${API_BASE}/api/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const data = (await res.json().catch(() => null)) as { error?: { message?: string } } | null;
    throw new Error(data?.error?.message ?? "회원가입에 실패했습니다.");
  }
  return res.json() as Promise<{ user: { id: string; email: string; name: string } }>;
}

export default function RegisterPage() {
  const router = useRouter();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [birthDate, setBirthDate] = useState("");
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [agreedToPrivacy, setAgreedToPrivacy] = useState(false);
  const [agreedToAge14, setAgreedToAge14] = useState(false);
  const [agreedToOverseas, setAgreedToOverseas] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState("");

  const allConsented = agreedToTerms && agreedToPrivacy && agreedToAge14 && agreedToOverseas;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!allConsented) {
      setFeedback("필수 동의 항목을 모두 확인해 주세요.");
      return;
    }
    if (password.length < 10) {
      setFeedback("비밀번호는 10자 이상이어야 합니다.");
      return;
    }
    setSubmitting(true);
    setFeedback("");
    try {
      const res = await registerUser({
        email,
        password,
        name,
        birthDate,
        agreedToTerms: true,
        agreedToPrivacy: true,
        agreedToAge14: true,
        agreedToOverseasTransfer: true,
      });
      setStoredAuthSession({ user: res.user });
      router.replace("/");
    } catch (err) {
      setFeedback(err instanceof Error ? err.message : "회원가입에 실패했습니다.");
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
            <h1>지금 바로 시작해 보세요.</h1>
            <p>SNS 숏폼 영상을 사진 몇 장으로 만들 수 있습니다.</p>
          </div>
        </div>

        <div className="auth-panel__form">
          <div className="auth-copy">
            <strong>회원가입</strong>
            {feedback && <p className="auth-feedback auth-feedback--error">{feedback}</p>}
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <label className="auth-field">
              <span>이름</span>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                autoComplete="name"
                required
              />
            </label>
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
              <span>비밀번호 (10자 이상)</span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="new-password"
                minLength={10}
                required
              />
            </label>
            <label className="auth-field">
              <span>생년월일</span>
              <input
                type="date"
                value={birthDate}
                onChange={(e) => setBirthDate(e.target.value)}
                max={new Date().toISOString().split("T")[0]}
                required
              />
            </label>

            <div className="auth-consents">
              <label className="auth-field auth-field--checkbox">
                <input
                  type="checkbox"
                  checked={agreedToAge14}
                  onChange={(e) => setAgreedToAge14(e.target.checked)}
                />
                <span>[필수] 만 14세 이상입니다</span>
              </label>
              <label className="auth-field auth-field--checkbox">
                <input
                  type="checkbox"
                  checked={agreedToTerms}
                  onChange={(e) => setAgreedToTerms(e.target.checked)}
                />
                <span>
                  [필수]{" "}
                  <Link href="/terms" target="_blank" rel="noopener noreferrer">
                    이용약관
                  </Link>
                  에 동의합니다
                </span>
              </label>
              <label className="auth-field auth-field--checkbox">
                <input
                  type="checkbox"
                  checked={agreedToPrivacy}
                  onChange={(e) => setAgreedToPrivacy(e.target.checked)}
                />
                <span>
                  [필수]{" "}
                  <Link href="/privacy" target="_blank" rel="noopener noreferrer">
                    개인정보 수집 및 이용
                  </Link>
                  에 동의합니다
                </span>
              </label>
              <label className="auth-field auth-field--checkbox">
                <input
                  type="checkbox"
                  checked={agreedToOverseas}
                  onChange={(e) => setAgreedToOverseas(e.target.checked)}
                />
                <span>[필수] 개인정보의 국외 이전에 동의합니다</span>
              </label>
            </div>

            <div className="auth-actions">
              <button type="submit" className="button button-primary" disabled={submitting || !allConsented}>
                {submitting ? "처리 중" : "회원가입"}
              </button>
              <Link href="/login" className="button button-secondary">
                로그인으로 돌아가기
              </Link>
            </div>
          </form>

          <div className="auth-links">
            <span style={{ color: "var(--muted)" }}>이미 계정이 있으신가요?</span>
            <Link href="/login">로그인</Link>
          </div>
        </div>
      </section>
    </main>
  );
}

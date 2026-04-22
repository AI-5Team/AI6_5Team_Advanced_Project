"use client";

import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ?? "";

async function verifyEmailToken(token: string) {
  const res = await fetch(`${API_BASE}/api/auth/verify-email`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ token }),
  });
  if (!res.ok) {
    const data = (await res.json().catch(() => null)) as { error?: { message?: string } } | null;
    throw new Error(data?.error?.message ?? "인증에 실패했습니다.");
  }
  return res.json();
}

export default function EmailVerifyPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") ?? "";
  const [status, setStatus] = useState<"pending" | "success" | "error">("pending");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("유효하지 않은 인증 링크입니다.");
      return;
    }
    verifyEmailToken(token)
      .then(() => setStatus("success"))
      .catch((err: unknown) => {
        setStatus("error");
        setMessage(err instanceof Error ? err.message : "인증에 실패했습니다.");
      });
  }, [token]);

  return (
    <main className="auth-screen">
      <section className="auth-panel auth-panel--loading">
        {status === "pending" && <strong>이메일 인증 중입니다...</strong>}
        {status === "success" && (
          <>
            <strong>이메일 인증이 완료되었습니다.</strong>
            <p>이제 모든 서비스를 이용할 수 있습니다.</p>
            <Link href="/login" className="button button-primary">로그인하기</Link>
          </>
        )}
        {status === "error" && (
          <>
            <strong>인증에 실패했습니다.</strong>
            <p>{message}</p>
            <Link href="/login" className="button button-secondary">로그인으로 돌아가기</Link>
          </>
        )}
      </section>
    </main>
  );
}

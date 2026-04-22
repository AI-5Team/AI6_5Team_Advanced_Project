"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { logoutUser } from "@/lib/api";
import { clearStoredAuthSession } from "@/lib/auth";

export default function LogoutPage() {
  const router = useRouter();

  useEffect(() => {
    logoutUser()
      .catch(() => undefined)
      .finally(() => {
        clearStoredAuthSession();
        router.replace("/login");
      });
  }, [router]);

  return (
    <main className="auth-screen">
      <section className="auth-panel auth-panel--loading">
        <strong>로그아웃 처리 중입니다.</strong>
        <p>잠시 후 로그인 화면으로 이동합니다.</p>
      </section>
    </main>
  );
}

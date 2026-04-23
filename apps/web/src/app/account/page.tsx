"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { changePassword, deleteMyAccount } from "@/lib/api";
import { clearStoredAuthSession, getStoredAuthSession } from "@/lib/auth";

export default function AccountPage() {
  const router = useRouter();
  const session = getStoredAuthSession();

  const [pwForm, setPwForm] = useState({ currentPassword: "", newPassword: "", confirm: "" });
  const [pwFeedback, setPwFeedback] = useState("");
  const [pwSubmitting, setPwSubmitting] = useState(false);

  const [deleteConfirm, setDeleteConfirm] = useState("");
  const [deleteSubmitting, setDeleteSubmitting] = useState(false);
  const [deleteFeedback, setDeleteFeedback] = useState("");

  const handleChangePassword = async (e: FormEvent) => {
    e.preventDefault();
    if (pwForm.newPassword !== pwForm.confirm) {
      setPwFeedback("새 비밀번호가 일치하지 않습니다.");
      return;
    }
    if (pwForm.newPassword.length < 10) {
      setPwFeedback("새 비밀번호는 10자 이상이어야 합니다.");
      return;
    }
    setPwSubmitting(true);
    setPwFeedback("");
    try {
      await changePassword({ currentPassword: pwForm.currentPassword, newPassword: pwForm.newPassword });
      setPwFeedback("비밀번호가 변경되었습니다. 다시 로그인해 주세요.");
      clearStoredAuthSession();
      setTimeout(() => router.replace("/login"), 1500);
    } catch (err) {
      setPwFeedback(err instanceof Error ? err.message : "비밀번호 변경에 실패했습니다.");
    } finally {
      setPwSubmitting(false);
    }
  };

  const handleDeleteAccount = async (e: FormEvent) => {
    e.preventDefault();
    if (deleteConfirm !== "탈퇴합니다") {
      setDeleteFeedback("확인 문구를 정확히 입력해 주세요.");
      return;
    }
    setDeleteSubmitting(true);
    setDeleteFeedback("");
    try {
      const res = await deleteMyAccount();
      clearStoredAuthSession();
      setDeleteFeedback(`회원 탈퇴가 접수되었습니다. 데이터는 ${new Date(res.scheduledDeletionAt).toLocaleDateString("ko-KR")} 이후 삭제됩니다.`);
      setTimeout(() => router.replace("/login"), 3000);
    } catch (err) {
      setDeleteFeedback(err instanceof Error ? err.message : "탈퇴 처리에 실패했습니다.");
    } finally {
      setDeleteSubmitting(false);
    }
  };

  return (
    <main className="account-page">
      <header className="account-page__header">
        <Link href="/" className="legal-page__back">← 홈으로</Link>
        <h1>계정 설정</h1>
        {session?.user && (
          <p className="account-page__email">{session.user.name} · {session.user.email}</p>
        )}
      </header>

      <div className="account-page__sections">
        <section className="account-section">
          <h2>비밀번호 변경</h2>
          <form className="auth-form" onSubmit={handleChangePassword}>
            <label className="auth-field">
              <span>현재 비밀번호</span>
              <input
                type="password"
                value={pwForm.currentPassword}
                onChange={(e) => setPwForm((f) => ({ ...f, currentPassword: e.target.value }))}
                autoComplete="current-password"
                required
              />
            </label>
            <label className="auth-field">
              <span>새 비밀번호 (10자 이상)</span>
              <input
                type="password"
                value={pwForm.newPassword}
                onChange={(e) => setPwForm((f) => ({ ...f, newPassword: e.target.value }))}
                autoComplete="new-password"
                minLength={10}
                required
              />
            </label>
            <label className="auth-field">
              <span>새 비밀번호 확인</span>
              <input
                type="password"
                value={pwForm.confirm}
                onChange={(e) => setPwForm((f) => ({ ...f, confirm: e.target.value }))}
                autoComplete="new-password"
                minLength={10}
                required
              />
            </label>
            {pwFeedback && (
              <p className={pwFeedback.includes("변경되었습니다") ? "auth-feedback" : "auth-feedback auth-feedback--error"}>
                {pwFeedback}
              </p>
            )}
            <div className="auth-actions">
              <button type="submit" className="button button-primary" disabled={pwSubmitting}>
                {pwSubmitting ? "변경 중" : "비밀번호 변경"}
              </button>
            </div>
          </form>
        </section>

        <section className="account-section account-section--danger">
          <h2>회원 탈퇴</h2>
          <p className="account-section__desc">
            탈퇴 후 30일 이내에는 계정이 완전히 삭제되지 않습니다.
            탈퇴 신청 후 30일이 지나면 모든 데이터가 영구 삭제됩니다.
          </p>
          <form className="auth-form" onSubmit={handleDeleteAccount}>
            <label className="auth-field">
              <span>확인을 위해 <strong>탈퇴합니다</strong> 를 입력해 주세요</span>
              <input
                type="text"
                value={deleteConfirm}
                onChange={(e) => setDeleteConfirm(e.target.value)}
                placeholder="탈퇴합니다"
                required
              />
            </label>
            {deleteFeedback && (
              <p className={deleteFeedback.includes("접수") ? "auth-feedback" : "auth-feedback auth-feedback--error"}>
                {deleteFeedback}
              </p>
            )}
            <div className="auth-actions">
              <button
                type="submit"
                className="button button-danger"
                disabled={deleteSubmitting || deleteConfirm !== "탈퇴합니다"}
              >
                {deleteSubmitting ? "처리 중" : "회원 탈퇴"}
              </button>
            </div>
          </form>
        </section>
      </div>
    </main>
  );
}

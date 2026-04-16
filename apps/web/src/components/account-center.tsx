"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

import {
  callbackSocialAccount,
  connectSocialAccount,
  getSocialAccounts,
} from "@/lib/api";
import type { Channel, SocialAccountSummary } from "@/lib/contracts";
import {
  CHANNEL_LABELS,
  formatDateTime,
  socialStatusHint,
  socialStatusLabel,
  statusTone,
} from "@/lib/display";

const CHANNEL_ORDER: Channel[] = ["instagram", "youtube_shorts", "tiktok"];

function actionLabel(status: SocialAccountSummary["status"]) {
  if (status === "connected") return "다시 확인";
  if (status === "expired" || status === "permission_error") return "다시 연결";
  if (status === "connecting") return "연결 확인";
  return "연결 시작";
}

export function AccountCenter() {
  const [accounts, setAccounts] = useState<SocialAccountSummary[]>([]);
  const [feedback, setFeedback] = useState(
    "연결이 안 되어 있어도 콘텐츠 만들기는 계속할 수 있습니다.",
  );

  const sortedAccounts = useMemo(
    () =>
      [...accounts].sort(
        (left, right) =>
          CHANNEL_ORDER.indexOf(left.channel) - CHANNEL_ORDER.indexOf(right.channel),
      ),
    [accounts],
  );
  const connectedCount = useMemo(
    () => sortedAccounts.filter((account) => account.status === "connected").length,
    [sortedAccounts],
  );
  const reconnectCount = useMemo(
    () =>
      sortedAccounts.filter(
        (account) =>
          account.status === "expired" || account.status === "permission_error",
      ).length,
    [sortedAccounts],
  );

  const loadAccounts = async () => {
    const response = await getSocialAccounts();
    setAccounts(response.items);
  };

  const handleConnect = async (channel: Channel) => {
    const connection = await connectSocialAccount(channel);
    const callbackUrl = new URL(connection.redirectUrl, window.location.origin);
    await callbackSocialAccount(channel, {
      code: callbackUrl.searchParams.get("code") ?? undefined,
      state: callbackUrl.searchParams.get("state") ?? undefined,
    });
    await loadAccounts();
    setFeedback(`${CHANNEL_LABELS[channel].title} 연결 상태를 다시 확인했습니다.`);
  };

  useEffect(() => {
    void loadAccounts().catch((error) => {
      setFeedback(
        error instanceof Error
          ? error.message
          : "채널 연결 상태를 불러오지 못했습니다.",
      );
    });
  }, []);

  return (
    <main className="app-shell workspace-page">
      <section className="workspace-overview">
        <div className="workspace-overview__main">
          <span className="workspace-label">채널 연결</span>
          <h1>채널 연결은 나중에 붙입니다.</h1>
          <p>
            지금은 연결 상태만 확인해 두고, 결과 만들기와 업로드 준비를 먼저 진행합니다.
          </p>
        </div>
        <div className="workspace-overview__stats">
          <div className="workspace-inline-stats">
            <div className="workspace-stat">
              <span>연결된 채널</span>
              <strong>{connectedCount}개</strong>
            </div>
            <div className="workspace-stat">
              <span>다시 확인 필요</span>
              <strong>{reconnectCount}개</strong>
            </div>
            <div className="workspace-stat">
              <span>기본 채널</span>
              <strong>인스타그램</strong>
            </div>
          </div>
          <div className="workspace-note">
            <strong>현재 안내</strong>
            <p>{feedback}</p>
          </div>
        </div>
      </section>

      <div className="workspace-columns">
        <section className="workspace-rail">
          <div className="workspace-section">
            <div className="workspace-section-head">
              <div>
                <h2>채널별 상태</h2>
                <p>연결 여부와 재확인 필요 여부만 빠르게 봅니다.</p>
              </div>
            </div>

            {sortedAccounts.length > 0 ? (
              <div className="account-list">
                {sortedAccounts.map((account) => (
                  <div key={account.channel} className="account-row">
                    <div className="account-row__top">
                      <div className="account-row__title">
                        <div className="account-row__header">
                          <strong>{CHANNEL_LABELS[account.channel].title}</strong>
                          <span
                            className={`tone-badge tone-badge--${statusTone(account.status)}`}
                          >
                            {socialStatusLabel(account.status)}
                          </span>
                        </div>
                        <p>{socialStatusHint(account.channel, account.status)}</p>
                      </div>
                      <button
                        className="button button-secondary"
                        onClick={() => void handleConnect(account.channel)}
                      >
                        {actionLabel(account.status)}
                      </button>
                    </div>
                    <div className="account-row__meta">
                      <span>연결된 계정: {account.accountName ?? "아직 없음"}</span>
                      <span>최근 확인: {formatDateTime(account.lastSyncedAt)}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <strong>채널 상태를 아직 불러오지 못했습니다.</strong>
                <p>잠시 뒤 다시 확인하거나, 일단 만들기 화면에서 작업을 계속하셔도 됩니다.</p>
              </div>
            )}
          </div>
        </section>

        <section className="workspace-main">
          <div className="workspace-section">
            <div className="workspace-section-head">
              <div>
                <h2>어떻게 쓰나요</h2>
                <p>지금 필요한 순서만 남겼습니다.</p>
              </div>
            </div>

            <div className="workspace-kpi-grid">
              <div className="workspace-kpi">
                <span className="workspace-kpi__label">지금 기본 채널</span>
                <strong>인스타그램</strong>
                <p>자동 게시를 가장 먼저 준비하는 채널은 인스타그램입니다.</p>
              </div>
              <div className="workspace-kpi">
                <span className="workspace-kpi__label">연결이 안 되어도 가능</span>
                <strong>업로드 준비물로 계속 진행</strong>
                <p>
                  자동 게시가 막히면 캡션, 해시태그, 영상 파일을 정리해서 바로 올릴 수 있게
                  도와드립니다.
                </p>
              </div>
              <div className="workspace-kpi">
                <span className="workspace-kpi__label">나머지 채널</span>
                <strong>유튜브 쇼츠, 틱톡은 나중에 확장</strong>
                <p>
                  지금은 연결 여부를 참고만 하고, 실제 사용은 업로드 준비물 중심으로 안내하는
                  편이 더 안정적입니다.
                </p>
              </div>
            </div>

            <div className="workspace-note-stack">
              <div className="workspace-note">
                <strong>권장 순서</strong>
                <span>1. 콘텐츠를 먼저 만듭니다.</span>
                <span>2. 업로드 준비물로 실제 게시를 진행합니다.</span>
                <span>3. 자동 게시가 필요해질 때만 채널 연결을 다시 확인합니다.</span>
              </div>
            </div>

            <div className="history-actions">
              <Link href="/" className="button button-primary">
                만들기 화면으로 돌아가기
              </Link>
              <button className="button button-secondary" onClick={() => void loadAccounts()}>
                상태 다시 확인
              </button>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

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

function tokenExpiryNote(account: SocialAccountSummary): string | null {
  if (!account.tokenExpiresAt) return null;
  const exp = new Date(account.tokenExpiresAt);
  const now = new Date();
  const diffMs = exp.getTime() - now.getTime();
  if (diffMs <= 0) return "토큰 만료됨";
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  if (diffDays < 1) return "오늘 만료 예정";
  if (diffDays <= 3) return `${diffDays}일 후 만료 예정`;
  return null;
}

export function AccountCenter() {
  const [accounts, setAccounts] = useState<SocialAccountSummary[]>([]);
  const [globalFeedback, setGlobalFeedback] = useState<string | null>(null);
  const [channelErrors, setChannelErrors] = useState<Partial<Record<Channel, string>>>({});
  const [loadingChannels, setLoadingChannels] = useState<Set<Channel>>(new Set());

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
    setLoadingChannels((prev) => new Set(prev).add(channel));
    setChannelErrors((prev) => { const next = { ...prev }; delete next[channel]; return next; });
    try {
      const connection = await connectSocialAccount(channel);
      const callbackUrl = new URL(connection.redirectUrl, window.location.origin);
      await callbackSocialAccount(channel, {
        code: callbackUrl.searchParams.get("code") ?? undefined,
        state: callbackUrl.searchParams.get("state") ?? undefined,
      });
      await loadAccounts();
      setGlobalFeedback(`${CHANNEL_LABELS[channel].title} 연결 상태를 확인했습니다.`);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "연결 중 오류가 발생했습니다.";
      setChannelErrors((prev) => ({ ...prev, [channel]: msg }));
    } finally {
      setLoadingChannels((prev) => { const next = new Set(prev); next.delete(channel); return next; });
    }
  };

  useEffect(() => {
    void loadAccounts().catch((error) => {
      setGlobalFeedback(
        error instanceof Error
          ? error.message
          : "채널 연결 상태를 불러오지 못했습니다.",
      );
    });
  }, []);

  const hasReconnectNeeded = reconnectCount > 0;

  return (
    <main className="app-shell workspace-page">
      <section className="workspace-overview">
        <div className="workspace-overview__main">
          <span className="workspace-label">채널 연결</span>
          <h1>SNS 채널 연결 상태</h1>
          <p>
            연결된 채널에서 자동 게시를 바로 사용할 수 있습니다.
            연결이 없어도 업로드 보조 방식으로 콘텐츠를 계속 진행할 수 있습니다.
          </p>
        </div>
        <div className="workspace-overview__stats">
          <div className="workspace-inline-stats">
            <div className="workspace-stat">
              <span>연결된 채널</span>
              <strong>{connectedCount}개</strong>
            </div>
            <div className="workspace-stat">
              <span>재연결 필요</span>
              <strong
                className={hasReconnectNeeded ? "tone-text--danger" : undefined}
              >
                {reconnectCount}개
              </strong>
            </div>
            <div className="workspace-stat">
              <span>기본 채널</span>
              <strong>인스타그램</strong>
            </div>
          </div>
          {hasReconnectNeeded && (
            <div className="workspace-note workspace-note--warn">
              <strong>재연결이 필요한 채널이 있습니다</strong>
              <p>만료되거나 권한 오류가 발생한 채널은 자동 게시가 중단됩니다. 아래에서 다시 연결해 주세요.</p>
            </div>
          )}
          {!hasReconnectNeeded && globalFeedback && (
            <div className="workspace-note">
              <strong>안내</strong>
              <p>{globalFeedback}</p>
            </div>
          )}
        </div>
      </section>

      <div className="workspace-columns">
        <section className="workspace-rail">
          <div className="workspace-section">
            <div className="workspace-section-head">
              <div>
                <h2>채널별 상태</h2>
                <p>연결 여부와 재확인 필요 여부를 확인합니다.</p>
              </div>
            </div>

            {sortedAccounts.length > 0 ? (
              <div className="account-list">
                {sortedAccounts.map((account) => {
                  const isLoading = loadingChannels.has(account.channel);
                  const channelError = channelErrors[account.channel];
                  const expiryNote = tokenExpiryNote(account);
                  return (
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
                            {expiryNote && (
                              <span className="tone-badge tone-badge--warning">
                                {expiryNote}
                              </span>
                            )}
                          </div>
                          <p>{socialStatusHint(account.channel, account.status)}</p>
                          {channelError && (
                            <p className="account-row__error">{channelError}</p>
                          )}
                        </div>
                        <button
                          className="button button-secondary"
                          disabled={isLoading}
                          onClick={() => void handleConnect(account.channel)}
                        >
                          {isLoading ? "처리 중…" : actionLabel(account.status)}
                        </button>
                      </div>
                      <div className="account-row__meta">
                        <span>연결된 계정: {account.accountName ?? "아직 없음"}</span>
                        <span>최근 확인: {formatDateTime(account.lastSyncedAt)}</span>
                        {account.tokenExpiresAt && account.status === "connected" && (
                          <span>토큰 만료: {formatDateTime(account.tokenExpiresAt)}</span>
                        )}
                      </div>
                    </div>
                  );
                })}
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
                <h2>연결 안내</h2>
                <p>지금 필요한 순서만 남겼습니다.</p>
              </div>
            </div>

            <div className="workspace-kpi-grid">
              <div className="workspace-kpi">
                <span className="workspace-kpi__label">기본 채널</span>
                <strong>인스타그램</strong>
                <p>자동 게시를 가장 먼저 준비하는 채널은 인스타그램입니다.</p>
              </div>
              <div className="workspace-kpi">
                <span className="workspace-kpi__label">연결 없이도 진행 가능</span>
                <strong>업로드 보조 방식</strong>
                <p>
                  자동 게시가 막히면 캡션, 해시태그, 영상 파일을 정리해서 직접 올릴 수 있게
                  안내합니다.
                </p>
              </div>
              <div className="workspace-kpi">
                <span className="workspace-kpi__label">나머지 채널</span>
                <strong>유튜브 쇼츠, 틱톡은 이후 확장</strong>
                <p>
                  지금은 연결 여부를 참고만 하고, 실제 사용은 업로드 보조 중심으로
                  안내합니다.
                </p>
              </div>
            </div>

            <div className="workspace-note-stack">
              <div className="workspace-note">
                <strong>권장 순서</strong>
                <span>1. 콘텐츠를 먼저 만듭니다.</span>
                <span>2. 업로드 보조로 실제 게시를 진행합니다.</span>
                <span>3. 자동 게시가 필요해질 때 채널 연결을 확인합니다.</span>
              </div>
            </div>

            <div className="history-actions">
              <Link href="/" className="button button-primary">
                만들기 화면으로 돌아가기
              </Link>
              <button className="button button-secondary" onClick={() => void loadAccounts()}>
                상태 새로고침
              </button>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

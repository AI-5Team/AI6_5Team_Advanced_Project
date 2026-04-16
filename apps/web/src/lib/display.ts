import {
  CHANNEL_TIERS,
  type BusinessType,
  type Channel,
  type ProjectStatus,
  type Purpose,
  type SocialAccountStatus,
  type Style,
} from "./contracts";

export const BUSINESS_LABELS: Record<BusinessType, string> = {
  cafe: "카페",
  restaurant: "음식점",
};

export const PURPOSE_LABELS: Record<Purpose, { title: string; hint: string }> = {
  new_menu: { title: "신메뉴", hint: "새 메뉴를 바로 보여줍니다." },
  promotion: { title: "할인/행사", hint: "오늘만 혜택을 강조합니다." },
  review: { title: "후기", hint: "짧은 반응을 전면에 둡니다." },
  location_push: { title: "방문 유도", hint: "동네와 위치를 함께 보여줍니다." },
};

export const STYLE_LABELS: Record<Style, { title: string; hint: string }> = {
  default: { title: "기본", hint: "짧고 또렷하게 정리합니다." },
  friendly: { title: "편안함", hint: "부드럽고 편하게 읽히는 톤입니다." },
  b_grade_fun: { title: "유쾌함", hint: "조금 더 가볍고 눈에 띄게 표현합니다." },
};

export const CHANNEL_LABELS: Record<Channel, { title: string; tier: string; hint: string }> = {
  instagram: {
    title: "인스타그램",
    tier: CHANNEL_TIERS.instagram,
    hint: "가장 먼저 준비하는 기본 채널입니다.",
  },
  youtube_shorts: {
    title: "유튜브 쇼츠",
    tier: CHANNEL_TIERS.youtube_shorts,
    hint: "지금은 업로드 준비물 중심으로 안내합니다.",
  },
  tiktok: {
    title: "틱톡",
    tier: CHANNEL_TIERS.tiktok,
    hint: "지금은 업로드 준비물 중심으로 안내합니다.",
  },
};

export function projectStatusLabel(status: ProjectStatus | string | null | undefined) {
  switch (status) {
    case "draft":
      return "초안";
    case "queued":
      return "대기";
    case "preprocessing":
      return "전처리";
    case "generating":
      return "생성 중";
    case "generated":
      return "완료";
    case "upload_assist":
      return "업로드 보조";
    case "scheduled":
      return "예약";
    case "publishing":
      return "게시 중";
    case "published":
      return "게시 완료";
    case "failed":
      return "실패";
    case "assist_required":
      return "보조 필요";
    case "assisted_completed":
      return "수동 완료";
    default:
      return status ?? "상태 없음";
  }
}

export function statusTone(status?: string | null) {
  if (!status) return "neutral";
  if (["published", "generated", "connected", "completed", "assisted_completed"].includes(status)) return "good";
  if (["failed", "assist_required", "expired", "permission_error"].includes(status)) return "danger";
  if (["queued", "processing", "publishing", "generating", "connecting", "upload_assist"].includes(status)) return "warning";
  return "neutral";
}

export function socialStatusLabel(status: SocialAccountStatus) {
  switch (status) {
    case "not_connected":
      return "미연동";
    case "connecting":
      return "연결 중";
    case "connected":
      return "연결됨";
    case "expired":
      return "만료";
    case "permission_error":
      return "권한 오류";
  }
}

export function socialStatusHint(channel: Channel, status: SocialAccountStatus) {
  if (status === "connected") {
    return channel === "instagram"
      ? "자동 게시와 업로드 보조를 모두 사용할 수 있습니다."
      : "연결은 되었지만 Phase 1에서는 업로드 보조 중심으로 사용합니다.";
  }
  if (status === "connecting") {
    return "브라우저 인증이 끝나면 자동으로 연결 상태로 전환됩니다.";
  }
  if (status === "expired") {
    return "토큰이 만료되어 다시 연결해야 합니다. 재연결 전에는 업로드 보조로만 진행하는 것이 안전합니다.";
  }
  if (status === "permission_error") {
    return "권한 범위가 부족합니다. 설정을 확인하거나 업로드 보조로 계속 진행해 주세요.";
  }
  return channel === "instagram"
    ? "자동 게시를 쓰려면 먼저 연결이 필요합니다."
    : "지금은 미연동이어도 업로드 보조 fallback으로 계속할 수 있습니다.";
}

export function formatDateTime(value: string | null | undefined) {
  if (!value) return "기록 없음";
  return new Intl.DateTimeFormat("ko-KR", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

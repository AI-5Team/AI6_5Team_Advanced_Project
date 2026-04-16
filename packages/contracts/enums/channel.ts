export const CHANNELS = ["instagram", "youtube_shorts", "tiktok"] as const;

export type Channel = (typeof CHANNELS)[number];

export const CHANNEL_LABELS: Record<Channel, string> = {
  instagram: "인스타그램",
  youtube_shorts: "유튜브 쇼츠",
  tiktok: "틱톡",
};

export const CHANNEL_SUPPORT_TIERS = {
  instagram: "ready",
  youtube_shorts: "experimental",
  tiktok: "experimental",
} as const;

export const CHANNEL_SUPPORT_TIER_VALUES = [
  "ready",
  "experimental",
  "unsupported",
] as const;

export type ChannelSupportTier = (typeof CHANNEL_SUPPORT_TIER_VALUES)[number];

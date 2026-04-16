export const BUSINESS_TYPES = ["cafe", "restaurant"] as const;

export type BusinessType = (typeof BUSINESS_TYPES)[number];

export const BUSINESS_TYPE_LABELS: Record<BusinessType, string> = {
  cafe: "카페",
  restaurant: "음식점",
};


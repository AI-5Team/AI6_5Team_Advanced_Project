export const PURPOSES = [
  "new_menu",
  "promotion",
  "review",
  "location_push",
] as const;

export type Purpose = (typeof PURPOSES)[number];

export const PURPOSE_LABELS: Record<Purpose, string> = {
  new_menu: "신메뉴 홍보",
  promotion: "할인/행사",
  review: "후기 강조",
  location_push: "위치 홍보",
};


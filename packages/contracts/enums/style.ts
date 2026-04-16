export const STYLES = ["default", "friendly", "b_grade_fun"] as const;

export type Style = (typeof STYLES)[number];

export const STYLE_LABELS: Record<Style, string> = {
  default: "기본",
  friendly: "친근함",
  b_grade_fun: "하찮고 웃김",
};


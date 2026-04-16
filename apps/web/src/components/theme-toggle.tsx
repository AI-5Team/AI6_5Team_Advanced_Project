"use client";

import { useEffect, useState } from "react";

const STORAGE_KEY = "studio-theme";

type Theme = "light" | "dark";

function resolveTheme(): Theme {
  if (typeof window === "undefined") {
    return "light";
  }

  const urlTheme = new URLSearchParams(window.location.search).get("theme");
  if (urlTheme === "light" || urlTheme === "dark") {
    return urlTheme;
  }

  const stored = window.localStorage.getItem(STORAGE_KEY);
  if (stored === "light" || stored === "dark") {
    return stored;
  }

  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
}

function applyTheme(theme: Theme) {
  document.documentElement.dataset.theme = theme;
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>("light");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const initialTheme = resolveTheme();
    applyTheme(initialTheme);
    setTheme(initialTheme);
    setMounted(true);
  }, []);

  const handleToggle = () => {
    const nextTheme: Theme = theme === "light" ? "dark" : "light";
    applyTheme(nextTheme);
    window.localStorage.setItem(STORAGE_KEY, nextTheme);
    setTheme(nextTheme);
  };

  return (
    <button
      type="button"
      className="theme-toggle"
      onClick={handleToggle}
      aria-label={mounted ? `${theme === "light" ? "다크" : "라이트"} 모드로 전환` : "테마 전환"}
    >
      <span className="theme-toggle__eyebrow">{mounted ? theme.toUpperCase() : "THEME"}</span>
      <strong>{mounted ? (theme === "light" ? "다크 모드" : "라이트 모드") : "테마 전환"}</strong>
    </button>
  );
}

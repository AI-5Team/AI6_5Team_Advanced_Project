"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ThemeToggle } from "@/components/theme-toggle";

const NAV_ITEMS = [
  {
    href: "/",
    label: "만들기",
    mobileLabel: "만들기",
  },
  {
    href: "/history",
    label: "작업 이력",
    mobileLabel: "이력",
  },
  {
    href: "/accounts",
    label: "채널",
    mobileLabel: "채널",
  },
  {
    href: "/account",
    label: "계정",
    mobileLabel: "계정",
  },
] as const;

export function AppNav() {
  const pathname = usePathname();
  if (pathname?.startsWith("/scene-frame")) {
    return null;
  }

  return (
    <>
      <header className="shell-nav-wrap">
        <div className="shell-nav">
          <Link href="/" className="shell-nav__brand" aria-label="가게 숏폼 스튜디오 홈">
            <strong>가게 숏폼 스튜디오</strong>
          </Link>

          <div className="shell-nav__actions">
            <ThemeToggle />

            <nav className="shell-nav__links" aria-label="주요 화면">
              {NAV_ITEMS.map((item) => {
                const active = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={
                      active
                        ? "shell-nav__link shell-nav__link--active"
                        : "shell-nav__link"
                    }
                  >
                    <strong>{item.label}</strong>
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      </header>

      <nav className="bottom-tab-nav" aria-label="모바일 주요 화면">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              aria-label={item.label}
              className={active ? "bottom-tab-nav__item bottom-tab-nav__item--active" : "bottom-tab-nav__item"}
            >
              {item.mobileLabel}
            </Link>
          );
        })}
      </nav>
    </>
  );
}

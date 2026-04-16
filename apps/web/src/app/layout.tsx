import type { Metadata, Viewport } from "next";
import { AuthGate } from "@/components/auth-gate";
import "./globals.css";

const themeInitScript = `
(() => {
  try {
    const key = "studio-theme";
    const urlTheme = new URLSearchParams(window.location.search).get("theme");
    const stored = window.localStorage.getItem(key);
    const theme =
      urlTheme === "light" || urlTheme === "dark"
        ? urlTheme
        : stored === "light" || stored === "dark"
        ? stored
        : window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light";
    document.documentElement.dataset.theme = theme;
  } catch (error) {
    document.documentElement.dataset.theme = "light";
  }
})();
`;

export const metadata: Metadata = {
  title: "가게 숏폼 만들기",
  description: "사진 몇 장으로 숏폼 영상과 업로드용 문구를 준비합니다.",
  applicationName: "가게 숏폼 만들기",
  icons: {
    icon: "/pwa-icon-192.svg",
    apple: "/pwa-icon-192.svg",
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "가게 숏폼 만들기",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  viewportFit: "cover",
  themeColor: "#0d1424",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="ko" data-theme="light" suppressHydrationWarning>
      <body>
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
        <AuthGate>{children}</AuthGate>
      </body>
    </html>
  );
}

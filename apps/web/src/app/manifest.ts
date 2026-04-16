import type { MetadataRoute } from "next";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "SNS 콘텐츠 생성 데모",
    short_name: "SNS 데모",
    description: "사진 업로드부터 숏폼 생성, 업로드 보조까지 모바일에서 확인하는 Phase 1 MVP",
    start_url: "/",
    display: "standalone",
    background_color: "#f6efe6",
    theme_color: "#f6efe6",
    lang: "ko-KR",
    orientation: "portrait",
    icons: [
      {
        src: "/pwa-icon-192.svg",
        sizes: "192x192",
        type: "image/svg+xml",
        purpose: "any",
      },
      {
        src: "/pwa-icon-512.svg",
        sizes: "512x512",
        type: "image/svg+xml",
        purpose: "any",
      },
    ],
    shortcuts: [
      {
        name: "새 콘텐츠 만들기",
        short_name: "만들기",
        url: "/",
      },
      {
        name: "생성 이력",
        short_name: "이력",
        url: "/history",
      },
      {
        name: "계정 연동",
        short_name: "계정",
        url: "/accounts",
      },
    ],
  };
}

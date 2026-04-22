import { type NextRequest, NextResponse } from "next/server";

const PUBLIC_PATHS = [
  "/login",
  "/register",
  "/logout",
  "/terms",
  "/privacy",
  "/email-verify",
  "/password-reset",
];

const API_ORIGIN = (() => {
  const raw = process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ?? "";
  if (!raw) return "";
  try {
    const { origin } = new URL(raw);
    return origin;
  } catch {
    return "";
  }
})();

const SECURITY_HEADERS: Record<string, string> = {
  "X-Frame-Options": "DENY",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
  "Content-Security-Policy": [
    "default-src 'self'",
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com",
    "img-src 'self' data: blob:",
    "media-src 'self' blob:",
    `connect-src 'self'${API_ORIGIN ? ` ${API_ORIGIN}` : ""}`,
    "frame-ancestors 'none'",
  ].join("; "),
};

function isPublicPath(pathname: string): boolean {
  return PUBLIC_PATHS.some((p) => pathname === p || pathname.startsWith(`${p}/`));
}

function addSecurityHeaders(response: NextResponse): NextResponse {
  Object.entries(SECURITY_HEADERS).forEach(([key, value]) => {
    response.headers.set(key, value);
  });
  return response;
}

export function middleware(request: NextRequest): NextResponse {
  const { pathname } = request.nextUrl;
  const sessionToken = request.cookies.get("session")?.value;

  // API 라우트는 미들웨어에서 처리하지 않음 (FastAPI가 담당)
  if (pathname.startsWith("/api/")) {
    return NextResponse.next();
  }

  // 공개 경로: 보안 헤더만 추가
  if (isPublicPath(pathname)) {
    return addSecurityHeaders(NextResponse.next());
  }

  // 정적 자산
  if (
    pathname.startsWith("/_next/") ||
    pathname.startsWith("/media/") ||
    pathname.startsWith("/sample-assets/") ||
    pathname.includes(".")
  ) {
    return NextResponse.next();
  }

  // 보호 경로: 세션 쿠키 없으면 /login으로 리다이렉트
  if (!sessionToken) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("next", pathname);
    return addSecurityHeaders(NextResponse.redirect(loginUrl));
  }

  return addSecurityHeaders(NextResponse.next());
}

export const config = {
  matcher: [
    "/((?!_next/static|_next/image|favicon.ico|pwa-icon).*)",
  ],
};

import { posix } from "node:path";
import { NextRequest, NextResponse } from "next/server";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ?? "";

function isAllowedStoragePath(storagePath: string) {
  return storagePath.startsWith("/media/");
}

function normalizedApiBaseUrl() {
  return apiBaseUrl.replace(/\/$/, "");
}

function safeFilename(filename: string | null, storagePath: string) {
  const fallback = posix.basename(storagePath) || "download.bin";
  const candidate = (filename || fallback).replace(/[^A-Za-z0-9._-]/g, "_");
  return candidate || fallback;
}

export async function GET(request: NextRequest) {
  const storagePath = request.nextUrl.searchParams.get("storagePath");
  const download = request.nextUrl.searchParams.get("download") === "1";
  const filename = request.nextUrl.searchParams.get("filename");

  if (!storagePath || !storagePath.startsWith("/")) {
    return NextResponse.json({ error: { code: "INVALID_STORAGE_PATH", message: "유효한 storagePath가 필요합니다." } }, { status: 400 });
  }

  if (!isAllowedStoragePath(storagePath)) {
    return NextResponse.json({ error: { code: "MEDIA_NOT_ALLOWED", message: "허용되지 않은 미디어 경로입니다." } }, { status: 403 });
  }

  if (!apiBaseUrl) {
    return NextResponse.json({ error: { code: "MEDIA_PROXY_UNAVAILABLE", message: "API base URL이 설정되지 않았습니다." } }, { status: 503 });
  }

  const upstreamUrl = new URL(storagePath, `${normalizedApiBaseUrl()}/`).toString();
  const upstream = await fetch(upstreamUrl, { cache: "no-store" });

  if (!upstream.ok) {
    return NextResponse.json({ error: { code: "MEDIA_FETCH_FAILED", message: "원본 미디어를 불러오지 못했습니다." } }, { status: upstream.status });
  }

  const headers = new Headers();
  headers.set("Content-Type", upstream.headers.get("content-type") ?? "application/octet-stream");
  headers.set("Cache-Control", "no-store");
  if (download) {
    headers.set("Content-Disposition", `attachment; filename="${safeFilename(filename, storagePath)}"`);
  }

  return new NextResponse(upstream.body, { status: 200, headers });
}

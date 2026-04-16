import { readFile } from "node:fs/promises";
import { extname, resolve } from "node:path";
import { NextRequest, NextResponse } from "next/server";

const REPO_ROOT = resolve(process.cwd(), "..", "..");
const ALLOWED_PREFIXES = ["/docs/sample/", "/samples/input/"];

function getContentType(filePath: string) {
  const extension = extname(filePath).toLowerCase();
  if (extension === ".png") {
    return "image/png";
  }
  if (extension === ".webp") {
    return "image/webp";
  }
  return "image/jpeg";
}

function isAllowedStoragePath(storagePath: string) {
  return ALLOWED_PREFIXES.some((prefix) => storagePath.startsWith(prefix));
}

export async function GET(request: NextRequest) {
  const storagePath = request.nextUrl.searchParams.get("storagePath");
  if (!storagePath || !storagePath.startsWith("/")) {
    return NextResponse.json({ error: { code: "INVALID_STORAGE_PATH", message: "유효한 storagePath가 필요합니다." } }, { status: 400 });
  }

  if (!isAllowedStoragePath(storagePath)) {
    return NextResponse.json({ error: { code: "MEDIA_NOT_ALLOWED", message: "허용되지 않은 로컬 미디어 경로입니다." } }, { status: 403 });
  }

  const filePath = resolve(REPO_ROOT, `.${storagePath}`);
  const buffer = await readFile(filePath);

  return new NextResponse(buffer, {
    headers: {
      "Content-Type": getContentType(filePath),
      "Cache-Control": "public, max-age=3600",
    },
  });
}

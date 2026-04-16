import { readFile } from "node:fs/promises";
import { extname, resolve } from "node:path";
import { NextResponse } from "next/server";

const SAMPLE_FILE_MAP: Record<string, string> = {
  katsu: "음식사진샘플(규카츠).jpg",
  beer: "음식사진샘플(맥주).jpg",
  ramen: "음식사진샘플(라멘).jpg",
  spicy: "음식사진샘플(순두부짬뽕).jpg",
  eel: "음식사진샘플(장어덮밥).jpg",
  takoyaki: "음식사진샘플(타코야키).jpg",
};

export async function GET(_: Request, context: { params: Promise<{ sample: string }> }) {
  const { sample } = await context.params;
  const fileName = SAMPLE_FILE_MAP[sample];
  if (!fileName) {
    return NextResponse.json({ error: { code: "SAMPLE_NOT_FOUND", message: "샘플 이미지를 찾을 수 없습니다." } }, { status: 404 });
  }

  const filePath = resolve(process.cwd(), "..", "..", "docs", "sample", fileName);
  const buffer = await readFile(filePath);
  const extension = extname(fileName).toLowerCase();
  const contentType = extension === ".png" ? "image/png" : "image/jpeg";

  return new NextResponse(buffer, {
    headers: {
      "Content-Type": contentType,
      "Cache-Control": "public, max-age=3600",
    },
  });
}

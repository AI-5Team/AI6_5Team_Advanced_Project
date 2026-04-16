import { NextResponse } from "next/server";
import { getProjectAssetPreview } from "@/lib/demo-store";
import { fail } from "@/lib/route-utils";

export async function GET(_: Request, { params }: { params: Promise<{ projectId: string; assetId: string }> }) {
  const { projectId, assetId } = await params;
  try {
    const preview = getProjectAssetPreview(projectId, assetId);
    return new NextResponse(preview.body, {
      headers: {
        "Content-Type": preview.contentType,
        "Cache-Control": "public, max-age=3600",
      },
    });
  } catch (error) {
    return fail("PROJECT_NOT_FOUND", error instanceof Error ? error.message : "프로젝트 자산을 찾을 수 없습니다.", 404);
  }
}

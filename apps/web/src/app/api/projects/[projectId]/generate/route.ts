import { startGeneration } from "@/lib/demo-store";
import { fail, ok } from "@/lib/route-utils";
import type { GenerateProjectRequest } from "@/lib/contracts";

export async function POST(request: Request, { params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  try {
    const body = (await request.json()) as GenerateProjectRequest;
    if (!body?.assetIds?.length || !body.templateId) {
      return fail("INVALID_INPUT", "생성 요청이 부족합니다.", 400);
    }
    return ok(startGeneration(projectId, body));
  } catch {
    return fail("PROJECT_NOT_FOUND", "프로젝트를 찾을 수 없습니다.", 404);
  }
}

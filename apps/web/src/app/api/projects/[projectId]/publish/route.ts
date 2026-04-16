import { publishProject } from "@/lib/demo-store";
import { fail, ok } from "@/lib/route-utils";
import type { PublishProjectRequest } from "@/lib/contracts";

export async function POST(request: Request, { params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  try {
    const body = (await request.json()) as PublishProjectRequest;
    if (!body?.variantId || !body?.channel || !body?.publishMode) {
      return fail("INVALID_INPUT", "게시 요청이 부족합니다.", 400);
    }
    return ok(publishProject(projectId, body));
  } catch (error) {
    if (error instanceof Error) {
      if (error.message === "INVALID_STATE_TRANSITION") {
        return fail("INVALID_STATE_TRANSITION", "게시할 결과물을 찾을 수 없습니다.", 422);
      }
      if (error.message === "INVALID_INPUT") {
        return fail("INVALID_INPUT", "게시 요청이 부족합니다.", 400);
      }
    }
    return fail("PROJECT_NOT_FOUND", "프로젝트를 찾을 수 없습니다.", 404);
  }
}

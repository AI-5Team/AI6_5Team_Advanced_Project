import { regenerateProject } from "@/lib/demo-store";
import { fail, ok } from "@/lib/route-utils";
import type { RegenerateProjectRequest } from "@/lib/contracts";

export async function POST(request: Request, { params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  try {
    const body = (await request.json()) as RegenerateProjectRequest;
    if (!body?.changeSet) {
      return fail("INVALID_INPUT", "재생성 변경값이 필요합니다.", 400);
    }
    return ok(regenerateProject(projectId, body.changeSet));
  } catch {
    return fail("PROJECT_NOT_FOUND", "프로젝트를 찾을 수 없습니다.", 404);
  }
}

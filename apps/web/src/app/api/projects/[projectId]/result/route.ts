import { getProjectResult } from "@/lib/demo-store";
import { fail, ok } from "@/lib/route-utils";

export async function GET(_: Request, { params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  try {
    return ok(getProjectResult(projectId));
  } catch (error) {
    const isState = error instanceof Error && error.message === "INVALID_STATE_TRANSITION";
    return fail(isState ? "INVALID_STATE_TRANSITION" : "PROJECT_NOT_FOUND", isState ? "아직 결과가 준비되지 않았습니다." : "프로젝트를 찾을 수 없습니다.", isState ? 422 : 404);
  }
}

import { getLatestUploadJobForProject, getProject } from "@/lib/demo-store";
import { fail, ok } from "@/lib/route-utils";

export async function GET(_: Request, { params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  try {
    getProject(projectId);
    return ok(getLatestUploadJobForProject(projectId));
  } catch {
    return fail("PROJECT_NOT_FOUND", "프로젝트를 찾을 수 없습니다.", 404);
  }
}

import { getProject } from "@/lib/demo-store";
import { fail, ok } from "@/lib/route-utils";

export async function GET(_: Request, { params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  try {
    const project = getProject(projectId);
    const { selectedTemplateId: _selectedTemplateId, selectedAssetIds: _selectedAssetIds, thumbnailText: _thumbnailText, latestGenerationRunId: _latestGenerationRunId, createdAt: _createdAt, updatedAt: _updatedAt, ...canonicalProject } = project;
    return ok(canonicalProject);
  } catch {
    return fail("PROJECT_NOT_FOUND", "프로젝트를 찾을 수 없습니다.", 404);
  }
}

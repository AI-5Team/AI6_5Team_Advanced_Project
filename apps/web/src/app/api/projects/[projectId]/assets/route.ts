import { addProjectAssets, getProjectAssets } from "@/lib/demo-store";
import { fail, ok } from "@/lib/route-utils";

export async function GET(_: Request, { params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  try {
    return ok({ projectId, assets: getProjectAssets(projectId) });
  } catch {
    return fail("PROJECT_NOT_FOUND", "프로젝트를 찾을 수 없습니다.", 404);
  }
}

export async function POST(request: Request, { params }: { params: Promise<{ projectId: string }> }) {
  const { projectId } = await params;
  try {
    const formData = await request.formData();
    const files = formData
      .getAll("files")
      .filter((entry): entry is File => entry instanceof File);

    if (files.length === 0) {
      return fail("INVALID_INPUT", "파일이 필요합니다.", 400);
    }

    return ok(await addProjectAssets(projectId, files), { status: 201 });
  } catch (error) {
    return fail("PROJECT_NOT_FOUND", error instanceof Error ? error.message : "프로젝트를 찾을 수 없습니다.", 404);
  }
}

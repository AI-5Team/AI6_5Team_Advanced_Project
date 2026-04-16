import { completeAssist } from "@/lib/demo-store";
import { fail, ok } from "@/lib/route-utils";

export async function POST(_: Request, { params }: { params: Promise<{ jobId: string }> }) {
  const { jobId } = await params;
  try {
    return ok(completeAssist(jobId));
  } catch {
    return fail("PROJECT_NOT_FOUND", "업로드 작업을 찾을 수 없습니다.", 404);
  }
}

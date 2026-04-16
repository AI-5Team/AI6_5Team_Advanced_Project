import { createProject, listProjects } from "@/lib/demo-store";
import { fail, ok } from "@/lib/route-utils";
import type { CreateProjectRequest } from "@/lib/contracts";

export async function GET(request: Request) {
  const url = new URL(request.url);
  const status = url.searchParams.get("status") ?? undefined;
  return ok({ items: listProjects(status as any), nextCursor: null, hasNext: false });
}

export async function POST(request: Request) {
  const body = (await request.json()) as CreateProjectRequest;
  if (!body?.businessType || !body?.regionName || !body?.purpose || !body?.style || !Array.isArray(body.channels) || body.channels.length === 0) {
    return fail("INVALID_INPUT", "생성 입력이 부족합니다.", 400);
  }
  return ok(createProject(body), { status: 201 });
}

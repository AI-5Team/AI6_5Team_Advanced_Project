import { getStoreProfile, updateStoreProfile } from "@/lib/demo-store";
import { fail, ok } from "@/lib/route-utils";
import type { UpdateStoreProfileRequest } from "@/lib/contracts";

export async function GET() {
  return ok(getStoreProfile());
}

export async function PUT(request: Request) {
  try {
    const body = (await request.json()) as UpdateStoreProfileRequest;
    if (!body?.businessType || !body?.regionName) {
      return fail("INVALID_INPUT", "매장 프로필 입력이 부족합니다.", 400);
    }
    return ok(updateStoreProfile(body));
  } catch {
    return fail("INVALID_INPUT", "매장 프로필 입력이 부족합니다.", 400);
  }
}

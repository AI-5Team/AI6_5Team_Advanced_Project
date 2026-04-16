import { listSocialAccounts } from "@/lib/demo-store";
import { ok } from "@/lib/route-utils";

export async function GET() {
  return ok(listSocialAccounts());
}

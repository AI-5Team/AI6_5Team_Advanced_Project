import { connectSocialAccount } from "@/lib/demo-store";
import { fail, ok } from "@/lib/route-utils";
import { CHANNELS, type Channel } from "@/lib/contracts";

function isChannel(value: string): value is Channel {
  return CHANNELS.includes(value as Channel);
}

export async function POST(_: Request, { params }: { params: Promise<{ channel: string }> }) {
  const { channel } = await params;
  if (!channel || !isChannel(channel)) {
    return fail("INVALID_INPUT", "채널이 필요합니다.", 400);
  }
  return ok(connectSocialAccount(channel));
}

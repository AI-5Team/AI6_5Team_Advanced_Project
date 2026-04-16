import { callbackSocialAccount } from "@/lib/demo-store";
import { fail, ok } from "@/lib/route-utils";
import { CHANNELS, type Channel } from "@/lib/contracts";

function isChannel(value: string): value is Channel {
  return CHANNELS.includes(value as Channel);
}

export async function GET(request: Request, { params }: { params: Promise<{ channel: string }> }) {
  const { channel } = await params;
  if (!channel || !isChannel(channel)) {
    return fail("INVALID_INPUT", "채널이 필요합니다.", 400);
  }
  const url = new URL(request.url);
  try {
    return ok(
      callbackSocialAccount(channel, {
        code: url.searchParams.get("code") ?? undefined,
        state: url.searchParams.get("state") ?? undefined,
      }),
    );
  } catch (error) {
    const code = error instanceof Error ? error.message : "OAUTH_CALLBACK_INVALID";
    return fail(code, "OAuth 콜백 검증에 실패했습니다.", 400);
  }
}

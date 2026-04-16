import { NextResponse } from "next/server";

export function ok<T>(body: T, init?: ResponseInit) {
  return NextResponse.json(body, init);
}

export function fail(code: string, message: string, status = 400, details?: Record<string, unknown>) {
  return NextResponse.json(
    {
      error: {
        code,
        message,
        ...(details ? { details } : {}),
      },
    },
    { status },
  );
}

"use client";

import { useEffect, useState } from "react";
import { getStoredAuthSession } from "@/lib/auth";
import { getMe } from "@/lib/api";
import type { AuthUser } from "@/lib/contracts";

export type SessionState =
  | { status: "loading" }
  | { status: "authenticated"; user: AuthUser }
  | { status: "unauthenticated" };

/**
 * Returns the current session state for use in client components.
 *
 * Usage:
 *   const session = useSession();
 *   if (session.status === "loading") return <Spinner />;
 *   if (session.status === "unauthenticated") redirect("/login");
 *   const { user } = session;
 */
export function useSession(): SessionState {
  const [state, setState] = useState<SessionState>({ status: "loading" });

  useEffect(() => {
    let cancelled = false;

    async function resolve() {
      const stored = getStoredAuthSession();
      if (!stored) {
        if (!cancelled) setState({ status: "unauthenticated" });
        return;
      }
      try {
        const me = await getMe();
        if (!cancelled) setState({ status: "authenticated", user: me });
      } catch {
        if (!cancelled) setState({ status: "unauthenticated" });
      }
    }

    void resolve();
    return () => { cancelled = true; };
  }, []);

  return state;
}

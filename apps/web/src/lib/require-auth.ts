import { cookies } from "next/headers";
import { redirect } from "next/navigation";

/**
 * Guards a server component or route handler: redirects to /login if no session cookie.
 * The middleware already redirects unauthenticated requests to protected pages,
 * but this helper lets individual server components double-check and access the raw token.
 *
 * Usage at the top of an async server page:
 *   const token = await requireAuth("/dashboard");
 */
export async function requireAuth(next?: string): Promise<string> {
  const cookieStore = await cookies();
  const sessionToken = cookieStore.get("session")?.value;
  if (!sessionToken) {
    const nextParam = next ? `?next=${encodeURIComponent(next)}` : "";
    redirect(`/login${nextParam}`);
  }
  return sessionToken;
}

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim() ?? "";

function normalizedApiBaseUrl() {
  return apiBaseUrl.replace(/\/$/, "");
}

export function resolveMediaUrl(storagePath: string) {
  if (!storagePath) {
    return storagePath;
  }

  if (storagePath.startsWith("data:") || storagePath.startsWith("http://") || storagePath.startsWith("https://")) {
    return storagePath;
  }

  if (storagePath.startsWith("/docs/sample/") || storagePath.startsWith("/samples/input/")) {
    return `/api/local-media?storagePath=${encodeURIComponent(storagePath)}`;
  }

  if (storagePath.startsWith("/api/")) {
    return storagePath;
  }

  if (storagePath.startsWith("/media/")) {
    return apiBaseUrl ? new URL(storagePath, `${normalizedApiBaseUrl()}/`).toString() : storagePath;
  }

  if (storagePath.startsWith("/projects/")) {
    const mediaPath = `/media${storagePath}`;
    return apiBaseUrl ? new URL(mediaPath, `${normalizedApiBaseUrl()}/`).toString() : mediaPath;
  }

  return storagePath;
}

export function buildMediaProxyUrl(storagePath: string, options?: { download?: boolean; filename?: string }) {
  const query = new URLSearchParams({ storagePath });
  if (options?.download) {
    query.set("download", "1");
  }
  if (options?.filename) {
    query.set("filename", options.filename);
  }
  return `/api/media-proxy?${query.toString()}`;
}

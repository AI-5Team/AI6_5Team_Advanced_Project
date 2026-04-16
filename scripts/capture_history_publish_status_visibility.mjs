import { mkdir, rm, writeFile, readFile, access } from "node:fs/promises";
import { constants as fsConstants } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { spawn } from "node:child_process";
import { createServer } from "node:net";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const WEB_APP_DIR = resolve(ROOT, "apps", "web");
const DEFAULT_PORT = Number(process.env.HISTORY_PUBLISH_STATUS_PORT ?? "3220");
const HOST = "127.0.0.1";
const OUTPUT_DIR = resolve(ROOT, "docs", "experiments", "artifacts", "exp-50-history-publish-status-visibility");
const SAMPLE_FILES = [
  resolve(ROOT, "docs", "sample", "음식사진샘플(규카츠).jpg"),
  resolve(ROOT, "docs", "sample", "음식사진샘플(맥주).jpg"),
];
const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
].filter(Boolean);

function delay(ms) {
  return new Promise((resolveDelay) => setTimeout(resolveDelay, ms));
}

function spawnLogged(command, args, options = {}) {
  return spawn(command, args, {
    cwd: ROOT,
    stdio: ["ignore", "pipe", "pipe"],
    shell: false,
    ...options,
  });
}

function quoteWindowsArg(arg) {
  return /[\s"]/u.test(arg) ? `"${arg.replaceAll('"', '\\"')}"` : arg;
}

function spawnNpm(args, options = {}) {
  if (process.platform === "win32") {
    const command = `npm ${args.map(quoteWindowsArg).join(" ")}`;
    return spawnLogged("cmd.exe", ["/d", "/s", "/c", command], options);
  }
  return spawnLogged("npm", args, options);
}

function collectProcessOutput(child, label) {
  let stdout = "";
  let stderr = "";
  child.stdout?.on("data", (chunk) => {
    stdout += chunk.toString();
  });
  child.stderr?.on("data", (chunk) => {
    stderr += chunk.toString();
  });
  child.on("error", (error) => {
    stderr += `\n[${label}] ${error.message}`;
  });
  return () => ({ stdout, stderr });
}

async function fileExists(path) {
  try {
    await access(path, fsConstants.F_OK);
    return true;
  } catch {
    return false;
  }
}

async function resolveChromePath() {
  for (const candidate of CHROME_CANDIDATES) {
    if (candidate && (await fileExists(candidate))) {
      return candidate;
    }
  }
  throw new Error("Chrome 또는 Edge 실행 파일을 찾지 못했습니다. CHROME_PATH를 설정해 주세요.");
}

async function runNpmCommand(args, label, options = {}) {
  const child = spawnNpm(args, options);
  const readOutput = collectProcessOutput(child, label);
  const code = await new Promise((resolveCode, rejectCode) => {
    child.on("close", resolveCode);
    child.on("error", rejectCode);
  });
  const output = readOutput();
  if (code !== 0) {
    throw new Error(`${label} failed (${code})\n${output.stdout}\n${output.stderr}`.trim());
  }
}

async function runCommand(command, args, label, options = {}) {
  const child = spawnLogged(command, args, options);
  const readOutput = collectProcessOutput(child, label);
  const code = await new Promise((resolveCode, rejectCode) => {
    child.on("close", resolveCode);
    child.on("error", rejectCode);
  });
  const output = readOutput();
  if (code !== 0) {
    throw new Error(`${label} failed (${code})\n${output.stdout}\n${output.stderr}`.trim());
  }
}

async function waitForServer(url, timeoutMs = 45000) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    try {
      const response = await fetch(url, { redirect: "manual" });
      if (response.ok) {
        return;
      }
    } catch {}
    await delay(1000);
  }
  throw new Error(`서버가 ${timeoutMs}ms 안에 준비되지 않았습니다: ${url}`);
}

async function findFreePort(startPort) {
  for (let port = startPort; port < startPort + 100; port += 1) {
    const isFree = await new Promise((resolveIsFree) => {
      const probe = createServer();
      probe.unref();
      probe.once("error", () => resolveIsFree(false));
      probe.listen(port, HOST, () => {
        probe.close(() => resolveIsFree(true));
      });
    });
    if (isFree) {
      return port;
    }
  }
  throw new Error(`사용 가능한 포트를 찾지 못했습니다. 시작 포트: ${startPort}`);
}

async function stopServer(server) {
  if (!server.pid) {
    return;
  }
  if (process.platform === "win32") {
    const child = spawnLogged("taskkill", ["/pid", String(server.pid), "/t", "/f"]);
    await new Promise((resolveClose) => child.on("close", resolveClose));
    return;
  }
  server.kill("SIGTERM");
  await delay(1200);
  if (!server.killed) {
    server.kill("SIGKILL");
  }
}

async function requestJson(url, init = {}) {
  const response = await fetch(url, {
    cache: "no-store",
    ...init,
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(`request failed: ${url}\n${message}`);
  }
  return response.json();
}

async function uploadSampleAssets(baseUrl, projectId) {
  const formData = new FormData();
  for (const filePath of SAMPLE_FILES) {
    const content = await readFile(filePath);
    formData.append("files", new Blob([content], { type: "image/jpeg" }), filePath.split("\\").at(-1));
  }
  return requestJson(`${baseUrl}/api/projects/${projectId}/assets`, {
    method: "POST",
    body: formData,
  });
}

async function waitForGenerated(baseUrl, projectId, timeoutMs = 30000) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    const statusPayload = await requestJson(`${baseUrl}/api/projects/${projectId}/status`);
    if (statusPayload.projectStatus === "generated" || statusPayload.result) {
      return statusPayload;
    }
    await delay(800);
  }
  throw new Error(`생성이 ${timeoutMs}ms 안에 완료되지 않았습니다: ${projectId}`);
}

async function captureWithChrome(chromePath, url, outputPath) {
  await mkdir(dirname(outputPath), { recursive: true });
  await rm(outputPath, { force: true });
  const args = [
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--force-device-scale-factor=1",
    "--window-size=1440,3200",
    "--virtual-time-budget=6000",
    `--screenshot=${outputPath}`,
    url,
  ];
  await runCommand(chromePath, args, `capture:${url}`);
}

async function buildWeb(envOverrides = {}) {
  await runNpmCommand(["run", "build:web"], "build:web", {
    env: {
      ...process.env,
      ...envOverrides,
    },
  });
}

async function main() {
  const chromePath = await resolveChromePath();
  const port = await findFreePort(DEFAULT_PORT);
  const baseUrl = `http://${HOST}:${port}`;
  await buildWeb({ NEXT_PUBLIC_API_BASE_URL: "" });
  await rm(OUTPUT_DIR, { recursive: true, force: true });
  await mkdir(OUTPUT_DIR, { recursive: true });

  const server = spawnNpm(["run", "start", "--", "--hostname", HOST, "--port", String(port)], {
    cwd: WEB_APP_DIR,
    env: {
      ...process.env,
      PORT: String(port),
      NEXT_PUBLIC_API_BASE_URL: "",
    },
  });
  const readServerOutput = collectProcessOutput(server, "history-publish-status:start");

  try {
    await waitForServer(`${baseUrl}/`);

    const connectResponse = await requestJson(`${baseUrl}/api/social-accounts/instagram/connect`, {
      method: "POST",
    });
    const redirectUrl = new URL(connectResponse.redirectUrl, `${baseUrl}/`);
    const state = redirectUrl.searchParams.get("state");
    const callbackResponse = await fetch(`${baseUrl}/api/social-accounts/instagram/callback?code=permission-error&state=${state}`, {
      cache: "no-store",
    });
    const callbackPayload = await callbackResponse.json().catch(() => null);

    const created = await requestJson(`${baseUrl}/api/projects`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        businessType: "restaurant",
        regionName: "성수동",
        detailLocation: "서울숲 골목",
        purpose: "promotion",
        style: "b_grade_fun",
        channels: ["instagram"],
      }),
    });
    const uploaded = await uploadSampleAssets(baseUrl, created.projectId);
    await requestJson(`${baseUrl}/api/projects/${created.projectId}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        assetIds: uploaded.assets.map((asset) => asset.assetId),
        templateId: "T02",
        quickOptions: {
          highlightPrice: true,
          shorterCopy: false,
          emphasizeRegion: false,
        },
      }),
    });
    await waitForGenerated(baseUrl, created.projectId);
    const result = await requestJson(`${baseUrl}/api/projects/${created.projectId}/result`);
    const publishResponse = await requestJson(`${baseUrl}/api/projects/${created.projectId}/publish`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        variantId: result.variantId,
        channel: "instagram",
        publishMode: "auto",
        captionOverride: result.copySet.captions[0],
        hashtags: result.copySet.hashtags,
        thumbnailText: "history publish status 확인",
      }),
    });
    const latestUploadJob = await requestJson(`${baseUrl}/api/projects/${created.projectId}/latest-upload-job`);
    const screenshotUrl = `${baseUrl}/history?projectId=${created.projectId}`;
    await captureWithChrome(chromePath, screenshotUrl, join(OUTPUT_DIR, "history-publish-status.png"));

    const summary = {
      capturedAt: new Date().toISOString(),
      baseUrl,
      chromePath,
      projectId: created.projectId,
      uploadJobId: publishResponse.uploadJobId,
      connectResponse,
      callbackStatus: callbackResponse.status,
      callbackPayload,
      publishResponse,
      latestUploadJob,
      screenshotUrl,
      checks: {
        selectedProjectPinned: screenshotUrl.includes(created.projectId),
        assistFallbackVisibleTarget: latestUploadJob?.status === "assist_required",
        latestUploadJobMessage: latestUploadJob?.error?.message ?? null,
      },
    };
    await writeFile(join(OUTPUT_DIR, "summary.json"), `${JSON.stringify(summary, null, 2)}\n`, "utf8");
  } finally {
    await stopServer(server);
    const { stdout, stderr } = readServerOutput();
    await writeFile(join(OUTPUT_DIR, "server.log"), `${stdout}\n${stderr}`.trim(), "utf8");
  }
}

main().catch((error) => {
  console.error(error instanceof Error ? error.message : String(error));
  process.exitCode = 1;
});

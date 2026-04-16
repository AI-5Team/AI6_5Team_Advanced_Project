import { mkdir, rm, writeFile, readFile } from "node:fs/promises";
import { dirname, join, resolve } from "node:path";
import { spawn } from "node:child_process";
import { createServer } from "node:net";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const WEB_APP_DIR = resolve(ROOT, "apps", "web");
const DEFAULT_PORT = Number(process.env.STALE_VARIANT_GUARD_PORT ?? "3225");
const HOST = "127.0.0.1";
const OUTPUT_DIR = resolve(ROOT, "docs", "experiments", "artifacts", "exp-60-stale-variant-publish-guard");
const SAMPLE_FILES = [
  resolve(ROOT, "docs", "sample", "음식사진샘플(규카츠).jpg"),
  resolve(ROOT, "docs", "sample", "음식사진샘플(맥주).jpg"),
];

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
  if (!server.pid) return;
  if (process.platform === "win32") {
    const child = spawnLogged("taskkill", ["/pid", String(server.pid), "/t", "/f"]);
    await new Promise((resolveClose) => child.on("close", resolveClose));
    return;
  }
  server.kill("SIGTERM");
  await delay(1200);
  if (!server.killed) server.kill("SIGKILL");
}

async function requestJson(url, init = {}) {
  const response = await fetch(url, {
    cache: "no-store",
    ...init,
  });
  const bodyText = await response.text();
  let body = null;
  try {
    body = bodyText ? JSON.parse(bodyText) : null;
  } catch {
    body = { raw: bodyText };
  }
  return { status: response.status, body };
}

async function uploadSampleAssets(baseUrl, projectId) {
  const formData = new FormData();
  for (const filePath of SAMPLE_FILES) {
    const content = await readFile(filePath);
    formData.append("files", new Blob([content], { type: "image/jpeg" }), filePath.split("\\").at(-1));
  }
  const response = await requestJson(`${baseUrl}/api/projects/${projectId}/assets`, {
    method: "POST",
    body: formData,
  });
  if (response.status !== 201) {
    throw new Error(`asset upload failed: ${JSON.stringify(response.body)}`);
  }
  return response.body;
}

async function waitForGenerated(baseUrl, projectId, timeoutMs = 30000) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    const statusPayload = await requestJson(`${baseUrl}/api/projects/${projectId}/status`);
    if (statusPayload.body?.projectStatus === "generated" || statusPayload.body?.result) {
      return statusPayload.body;
    }
    await delay(800);
  }
  throw new Error(`생성이 ${timeoutMs}ms 안에 완료되지 않았습니다: ${projectId}`);
}

async function buildWeb() {
  await runNpmCommand(["run", "build:web"], "build:web");
}

async function main() {
  await buildWeb();
  const port = await findFreePort(DEFAULT_PORT);
  const baseUrl = `http://${HOST}:${port}`;
  await rm(OUTPUT_DIR, { recursive: true, force: true });
  await mkdir(OUTPUT_DIR, { recursive: true });

  const server = spawnNpm(["run", "start", "--", "--hostname", HOST, "--port", String(port)], {
    cwd: WEB_APP_DIR,
    env: {
      ...process.env,
      PORT: String(port),
    },
  });
  const readServerOutput = collectProcessOutput(server, "stale-variant-guard:start");

  try {
    await waitForServer(`${baseUrl}/`);

    const created = await requestJson(`${baseUrl}/api/projects`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        businessType: "restaurant",
        regionName: "성수동",
        detailLocation: "서울숲 골목",
        purpose: "promotion",
        style: "b_grade_fun",
        channels: ["youtube_shorts"],
      }),
    });
    if (created.status !== 200 && created.status !== 201) {
      throw new Error(`create project failed: ${JSON.stringify(created.body)}`);
    }

    const projectId = created.body.projectId;
    const uploaded = await uploadSampleAssets(baseUrl, projectId);
    const generate = await requestJson(`${baseUrl}/api/projects/${projectId}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        assetIds: uploaded.assets.map((asset) => asset.assetId),
        templateId: "T02",
        quickOptions: {
          highlightPrice: false,
          shorterCopy: false,
          emphasizeRegion: false,
        },
      }),
    });
    if (generate.status !== 200 && generate.status !== 202) {
      throw new Error(`generate failed: ${JSON.stringify(generate.body)}`);
    }
    await waitForGenerated(baseUrl, projectId);
    const baselineResult = await requestJson(`${baseUrl}/api/projects/${projectId}/result`);
    if (baselineResult.status !== 200) {
      throw new Error(`baseline result failed: ${JSON.stringify(baselineResult.body)}`);
    }

    const regenerate = await requestJson(`${baseUrl}/api/projects/${projectId}/regenerate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        changeSet: {
          shorterCopy: true,
        },
      }),
    });
    if (regenerate.status !== 200 && regenerate.status !== 202) {
      throw new Error(`regenerate failed: ${JSON.stringify(regenerate.body)}`);
    }
    await waitForGenerated(baseUrl, projectId);
    const regeneratedResult = await requestJson(`${baseUrl}/api/projects/${projectId}/result`);
    if (regeneratedResult.status !== 200) {
      throw new Error(`regenerated result failed: ${JSON.stringify(regeneratedResult.body)}`);
    }

    const stalePublish = await requestJson(`${baseUrl}/api/projects/${projectId}/publish`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        variantId: baselineResult.body.variantId,
        channel: "youtube_shorts",
        publishMode: "assist",
        captionOverride: baselineResult.body.copySet.captions[0],
        hashtags: baselineResult.body.copySet.hashtags,
      }),
    });

    const freshPublish = await requestJson(`${baseUrl}/api/projects/${projectId}/publish`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        variantId: regeneratedResult.body.variantId,
        channel: "youtube_shorts",
        publishMode: "assist",
        captionOverride: regeneratedResult.body.copySet.captions[0],
        hashtags: regeneratedResult.body.copySet.hashtags,
      }),
    });

    const summary = {
      capturedAt: new Date().toISOString(),
      baseUrl,
      projectId,
      baselineVariantId: baselineResult.body.variantId,
      regeneratedVariantId: regeneratedResult.body.variantId,
      stalePublish,
      freshPublish,
      checks: {
        regenerationChangedVariant: baselineResult.body.variantId !== regeneratedResult.body.variantId,
        staleVariantRejected:
          stalePublish.status === 422 && stalePublish.body?.error?.code === "INVALID_STATE_TRANSITION",
        freshVariantAccepted:
          freshPublish.status === 200 ||
          (freshPublish.status === 202 &&
            (freshPublish.body?.status === "assist_required" || freshPublish.body?.status === "queued")),
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

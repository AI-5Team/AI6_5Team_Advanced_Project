import { mkdir, rm, writeFile, access } from "node:fs/promises";
import { constants as fsConstants } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { spawn } from "node:child_process";
import { createServer } from "node:net";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const WEB_APP_DIR = resolve(ROOT, "apps", "web");
const DEFAULT_PORT = Number(process.env.PROJECT_SCENE_PLAN_PORT ?? "3212");
const HOST = "127.0.0.1";
const OUTPUT_DIR = resolve(ROOT, "docs", "experiments", "artifacts", "exp-21-project-result-scene-plan-web-bridge");
const CHROME_CANDIDATES = [
  process.env.CHROME_PATH,
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
].filter(Boolean);

const SCENARIOS = [
  {
    key: "promotion",
    label: "T02 promotion",
    create: {
      businessType: "restaurant",
      regionName: "성수동",
      detailLocation: "서울숲 골목",
      purpose: "promotion",
      style: "b_grade_fun",
      channels: ["instagram"],
    },
    templateId: "T02",
    quickOptions: {
      highlightPrice: true,
      shorterCopy: false,
      emphasizeRegion: false,
    },
    assets: [
      { name: "규카츠", accent: "#e56a4c", background: "#f9eadf" },
      { name: "맥주", accent: "#ffd85c", background: "#fff4d7" },
    ],
    captures: [
      { sceneId: "s1", fileName: "promotion-opening.png" },
      { sceneId: "s4", fileName: "promotion-closing.png" },
    ],
  },
  {
    key: "review",
    label: "T04 review",
    create: {
      businessType: "restaurant",
      regionName: "합정",
      detailLocation: "상수역 근처",
      purpose: "review",
      style: "b_grade_fun",
      channels: ["instagram"],
    },
    templateId: "T04",
    quickOptions: {
      highlightPrice: false,
      shorterCopy: true,
      emphasizeRegion: false,
    },
    assets: [
      { name: "라멘", accent: "#ff7b3b", background: "#fbe7db" },
      { name: "타코야키", accent: "#e5ff39", background: "#f6f0cf" },
    ],
    captures: [
      { sceneId: "s1", fileName: "review-opening.png" },
      { sceneId: "s3", fileName: "review-closing.png" },
    ],
  },
];

function delay(ms) {
  return new Promise((resolveDelay) => setTimeout(resolveDelay, ms));
}

async function fileExists(path) {
  try {
    await access(path, fsConstants.F_OK);
    return true;
  } catch {
    return false;
  }
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

async function runNpmCommand(args, label) {
  const child = spawnNpm(args);
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

async function resolveChromePath() {
  for (const candidate of CHROME_CANDIDATES) {
    if (candidate && (await fileExists(candidate))) {
      return candidate;
    }
  }
  throw new Error("Chrome 또는 Edge 실행 파일을 찾지 못했습니다. CHROME_PATH를 설정해 주세요.");
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

async function waitForGenerated(baseUrl, projectId, timeoutMs = 20000) {
  const startedAt = Date.now();
  while (Date.now() - startedAt < timeoutMs) {
    const response = await fetch(`${baseUrl}/api/projects/${projectId}/status`, { cache: "no-store" });
    if (response.ok) {
      const payload = await response.json();
      if (payload.projectStatus === "generated" || payload.result) {
        return payload;
      }
    }
    await delay(800);
  }
  throw new Error(`생성이 ${timeoutMs}ms 안에 완료되지 않았습니다: ${projectId}`);
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

async function buildWeb() {
  await runNpmCommand(["run", "build:web"], "build:web");
}

async function captureWithChrome(chromePath, url, outputPath) {
  await mkdir(dirname(outputPath), { recursive: true });
  await rm(outputPath, { force: true });
  const args = [
    "--headless=new",
    "--disable-gpu",
    "--hide-scrollbars",
    "--force-device-scale-factor=1",
    "--window-size=1080,1920",
    `--screenshot=${outputPath}`,
    url,
  ];
  await runCommand(chromePath, args, `capture:${url}`);
}

async function stopServer(server) {
  if (!server.pid) {
    return;
  }
  if (process.platform === "win32") {
    try {
      await runCommand("taskkill", ["/pid", String(server.pid), "/t", "/f"], "taskkill");
      return;
    } catch {}
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

function buildSvgAsset(title, accent, background) {
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1440">
      <rect width="1080" height="1440" fill="${background}" />
      <rect x="92" y="92" width="896" height="1256" rx="52" fill="#fffdf8" stroke="#22170f" stroke-opacity="0.08" />
      <circle cx="290" cy="360" r="190" fill="${accent}" fill-opacity="0.28" />
      <circle cx="770" cy="1010" r="220" fill="${accent}" fill-opacity="0.18" />
      <text x="540" y="700" text-anchor="middle" fill="#22170f" font-size="88" font-weight="800" font-family="sans-serif">${title}</text>
      <text x="540" y="810" text-anchor="middle" fill="#6f5b49" font-size="40" font-weight="600" font-family="sans-serif">scenePlan demo asset</text>
    </svg>
  `.trim();
  return new Blob([svg], { type: "image/svg+xml" });
}

async function createProjectScenario(baseUrl, scenario) {
  const created = await requestJson(`${baseUrl}/api/projects`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(scenario.create),
  });

  const formData = new FormData();
  for (const asset of scenario.assets) {
    formData.append("files", buildSvgAsset(asset.name, asset.accent, asset.background), `${asset.name}.svg`);
  }

  const uploaded = await requestJson(`${baseUrl}/api/projects/${created.projectId}/assets`, {
    method: "POST",
    body: formData,
  });

  await requestJson(`${baseUrl}/api/projects/${created.projectId}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      assetIds: uploaded.assets.map((asset) => asset.assetId),
      templateId: scenario.templateId,
      quickOptions: scenario.quickOptions,
    }),
  });

  await waitForGenerated(baseUrl, created.projectId);
  const result = await requestJson(`${baseUrl}/api/projects/${created.projectId}/result`);
  const scenePlan = await requestJson(`${baseUrl}${result.scenePlan.url}`);

  return {
    projectId: created.projectId,
    uploadedAssetIds: uploaded.assets.map((asset) => asset.assetId),
    result,
    scenePlan,
  };
}

async function main() {
  await buildWeb();
  const chromePath = await resolveChromePath();
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
  const readServerOutput = collectProcessOutput(server, "project-scene-plan:start");

  try {
    await waitForServer(`${baseUrl}/`);
    const scenarios = [];
    for (const scenario of SCENARIOS) {
      const created = await createProjectScenario(baseUrl, scenario);
      const captures = [];
      for (const capture of scenario.captures) {
        const url = `${baseUrl}/scene-frame/${capture.sceneId}?projectId=${created.projectId}`;
        const outputPath = join(OUTPUT_DIR, capture.fileName);
        await captureWithChrome(chromePath, url, outputPath);
        captures.push({
          sceneId: capture.sceneId,
          url,
          outputPath,
        });
      }
      scenarios.push({
        key: scenario.key,
        label: scenario.label,
        projectId: created.projectId,
        scenePlanUrl: created.result.scenePlan?.url ?? null,
        sceneCount: created.scenePlan.sceneCount,
        captures,
      });
    }

    const summary = {
      capturedAt: new Date().toISOString(),
      baseUrl,
      chromePath,
      scenarios,
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

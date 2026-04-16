import { mkdir, rm, writeFile, access } from "node:fs/promises";
import { constants as fsConstants } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { spawn } from "node:child_process";
import { createServer } from "node:net";
import { fileURLToPath } from "node:url";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const DEFAULT_PORT = Number(process.env.SCENE_LAB_PORT ?? "3111");
const HOST = "127.0.0.1";
const OUTPUT_DIR = resolve(ROOT, "docs", "experiments", "artifacts", "exp-11-html-css-scene-capture");
const SCENES = [
  { id: "opening", fileName: "scene-opening.png" },
  { id: "review", fileName: "scene-review.png" },
  { id: "closing", fileName: "scene-closing.png" },
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
    } catch {
      // ignore until timeout
    }
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
    } catch {
      // fall back to regular kill below
    }
  }

  server.kill("SIGTERM");
  await delay(1200);
  if (!server.killed) {
    server.kill("SIGKILL");
  }
}

async function main() {
  await buildWeb();
  const chromePath = await resolveChromePath();
  const port = await findFreePort(DEFAULT_PORT);
  const baseUrl = `http://${HOST}:${port}`;
  await rm(OUTPUT_DIR, { recursive: true, force: true });
  await mkdir(OUTPUT_DIR, { recursive: true });

  const server = spawnNpm(
    ["--workspace", "apps/web", "run", "start", "--", "--hostname", HOST, "--port", String(port)],
    {
      env: {
        ...process.env,
        PORT: String(port),
      },
    },
  );

  const readServerOutput = collectProcessOutput(server, "scene-lab:start");

  try {
    await waitForServer(`${baseUrl}/scene-frame/opening`);

    const artifacts = [];
    for (const scene of SCENES) {
      const url = `${baseUrl}/scene-frame/${scene.id}`;
      const outputPath = join(OUTPUT_DIR, scene.fileName);
      await captureWithChrome(chromePath, url, outputPath);
      artifacts.push({
        sceneId: scene.id,
        url,
        outputPath,
      });
    }

    const summary = {
      capturedAt: new Date().toISOString(),
      baseUrl,
      chromePath,
      artifacts,
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

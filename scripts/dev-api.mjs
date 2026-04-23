import { spawn } from "node:child_process";

const env = {
  ...process.env,
  PYTHONPATH: process.env.PYTHONPATH || ".",
};

const args = [
  "run",
  "--project",
  "services/api",
  "uvicorn",
  "app.main:app",
  "--app-dir",
  "services/api",
  "--host",
  "127.0.0.1",
  "--port",
  "8000",
  "--reload",
];

const child = spawn("uv", args, {
  stdio: "inherit",
  shell: process.platform === "win32",
  env,
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }
  process.exit(code ?? 0);
});

child.on("error", (error) => {
  console.error(error);
  process.exit(1);
});

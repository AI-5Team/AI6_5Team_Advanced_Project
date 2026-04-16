from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FINETRAINERS_ROOT = Path(os.environ.get("FINETRAINERS_ROOT", Path(os.environ["TEMP"]) / "finetrainers-v020"))
DEFAULT_EXPERIMENT_ROOT = (
    REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-266-wan21-i2v-micro-lora-dry-run"
)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def build_command(
    *,
    python_executable: str,
    training_entrypoint: Path,
    training_config: Path,
    output_dir: Path,
    train_steps: int,
    gradient_accumulation_steps: int,
    log_level: str,
) -> list[str]:
    return [
        python_executable,
        str(training_entrypoint),
        "--parallel_backend",
        "accelerate",
        "--pp_degree",
        "1",
        "--dp_degree",
        "1",
        "--dp_shards",
        "1",
        "--cp_degree",
        "1",
        "--tp_degree",
        "1",
        "--model_name",
        "wan",
        "--pretrained_model_name_or_path",
        "Wan-AI/Wan2.1-I2V-14B-480P-Diffusers",
        "--dataset_config",
        str(training_config),
        "--dataset_shuffle_buffer_size",
        "1",
        "--enable_precomputation",
        "--precomputation_items",
        "18",
        "--precomputation_once",
        "--dataloader_num_workers",
        "0",
        "--flow_weighting_scheme",
        "logit_normal",
        "--training_type",
        "lora",
        "--seed",
        "42",
        "--batch_size",
        "1",
        "--train_steps",
        str(train_steps),
        "--rank",
        "8",
        "--lora_alpha",
        "16",
        "--target_modules",
        "blocks.*(to_q|to_k|to_v|to_out.0)",
        "--gradient_accumulation_steps",
        str(gradient_accumulation_steps),
        "--gradient_checkpointing",
        "--checkpointing_steps",
        str(max(train_steps, 20)),
        "--checkpointing_limit",
        "1",
        "--enable_slicing",
        "--enable_tiling",
        "--optimizer",
        "adamw",
        "--lr",
        "5e-5",
        "--lr_scheduler",
        "constant_with_warmup",
        "--lr_warmup_steps",
        "5",
        "--lr_num_cycles",
        "1",
        "--beta1",
        "0.9",
        "--beta2",
        "0.99",
        "--weight_decay",
        "1e-4",
        "--epsilon",
        "1e-8",
        "--max_grad_norm",
        "1.0",
        "--tracker_name",
        "finetrainers-wan21-i2v-micro-lora",
        "--output_dir",
        str(output_dir),
        "--init_timeout",
        "600",
        "--nccl_timeout",
        "600",
        "--report_to",
        "wandb",
        "--logging_steps",
        "1",
        "--allow_tf32",
        "--float32_matmul_precision",
        "high",
        "--verbose",
        log_level,
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Wan 2.1 I2V micro-LoRA dry run on Windows.")
    parser.add_argument("--finetrainers-root", type=Path, default=DEFAULT_FINETRAINERS_ROOT)
    parser.add_argument("--experiment-root", type=Path, default=DEFAULT_EXPERIMENT_ROOT)
    parser.add_argument("--train-steps", type=int, default=20)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=8)
    parser.add_argument("--log-level", default="1")
    parser.add_argument("--dry-only", action="store_true")
    args = parser.parse_args()

    if not args.finetrainers_root.exists():
        raise FileNotFoundError(f"finetrainers root not found: {args.finetrainers_root}")

    training_config = args.experiment_root / "training.json"
    if not training_config.exists():
        raise FileNotFoundError(f"training config not found: {training_config}")

    run_root = args.experiment_root / f"run_steps_{args.train_steps:03d}"
    run_root.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env["WANDB_MODE"] = "offline"
    env["FINETRAINERS_LOG_LEVEL"] = "INFO"
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["FINETRAINERS_ROOT"] = str(args.finetrainers_root)

    training_entrypoint = Path(__file__).resolve().with_name("wan21_i2v_micro_lora_train_entry.py")

    command = build_command(
        python_executable=sys.executable,
        training_entrypoint=training_entrypoint,
        training_config=training_config,
        output_dir=run_root,
        train_steps=args.train_steps,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        log_level=args.log_level,
    )

    write_text(run_root / "command.txt", subprocess.list2cmdline(command))
    (run_root / "meta.json").write_text(
        json.dumps(
            {
                "finetrainersRoot": str(args.finetrainers_root),
                "experimentRoot": str(args.experiment_root),
                "trainSteps": args.train_steps,
                "gradientAccumulationSteps": args.gradient_accumulation_steps,
                "pythonExecutable": sys.executable,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    if args.dry_only:
        print(run_root / "command.txt")
        return 0

    stdout_path = run_root / "run.stdout.log"
    stderr_path = run_root / "run.stderr.log"
    with stdout_path.open("w", encoding="utf-8") as stdout_file, stderr_path.open("w", encoding="utf-8") as stderr_file:
        completed = subprocess.run(
            command,
            cwd=args.finetrainers_root,
            env=env,
            stdout=stdout_file,
            stderr=stderr_file,
            text=True,
            encoding="utf-8",
        )

    print(run_root)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())

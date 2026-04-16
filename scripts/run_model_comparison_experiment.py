from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from services.worker.experiments.prompt_harness import (  # noqa: E402
    DEFAULT_ARTIFACT_ROOT,
    DEFAULT_TEMPLATE_SPEC_ROOT,
    get_model_comparison_definition,
    run_model_comparison_experiment,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run model-only comparison experiments on a fixed prompt baseline.")
    parser.add_argument("--experiment-id", default="EXP-23")
    parser.add_argument("--template-spec-root", type=Path, default=DEFAULT_TEMPLATE_SPEC_ROOT)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    args = parser.parse_args()

    artifact = run_model_comparison_experiment(
        experiment=get_model_comparison_definition(args.experiment_id),
        template_spec_root=args.template_spec_root,
        artifact_root=args.artifact_root,
    )
    print(json.dumps(artifact["comparison"], ensure_ascii=False, indent=2))
    print(f"artifact_path={artifact['artifact_path']}")


if __name__ == "__main__":
    main()

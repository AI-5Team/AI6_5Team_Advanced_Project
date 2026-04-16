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

from services.worker.experiments.prompt_harness import (
    DEFAULT_ARTIFACT_ROOT,
    DEFAULT_TEMPLATE_SPEC_ROOT,
    get_experiment_definition,
    resolve_api_key_env,
    run_experiment,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run prompt lever experiments without changing production generation.")
    parser.add_argument("--experiment-id", default="EXP-01")
    parser.add_argument("--template-spec-root", type=Path, default=DEFAULT_TEMPLATE_SPEC_ROOT)
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--api-key-env", default=None, help="Optional env var override. Defaults to provider-specific key.")
    args = parser.parse_args()
    experiment = get_experiment_definition(args.experiment_id)
    api_key_env = args.api_key_env or resolve_api_key_env(experiment.model.provider)

    artifact = run_experiment(
        experiment=experiment,
        template_spec_root=args.template_spec_root,
        artifact_root=args.artifact_root,
        api_key_env=api_key_env,
    )
    print(json.dumps(artifact["comparison"], ensure_ascii=False, indent=2))
    print(f"artifact_path={artifact['artifact_path']}")


if __name__ == "__main__":
    main()

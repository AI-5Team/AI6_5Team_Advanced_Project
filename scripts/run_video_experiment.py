from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from services.worker.experiments.video_harness import (  # noqa: E402
    DEFAULT_ARTIFACT_ROOT,
    get_video_experiment_definition,
    run_video_experiment,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run video-generation experiments without changing production renderer.")
    parser.add_argument("--experiment-id", default="EXP-03")
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    args = parser.parse_args()

    artifact = run_video_experiment(
        experiment=get_video_experiment_definition(args.experiment_id),
        artifact_root=args.artifact_root,
    )
    print(json.dumps(artifact, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

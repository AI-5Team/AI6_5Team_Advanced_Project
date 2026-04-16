from __future__ import annotations

import argparse
from pathlib import Path

from services.worker.pipelines.generation import run_generation_job
from services.worker.pipelines.publish import run_publish_job


def main() -> None:
    parser = argparse.ArgumentParser(description="Phase 1 worker CLI")
    parser.add_argument("--db-path", type=Path, required=True)
    parser.add_argument("--storage-root", type=Path, required=True)
    parser.add_argument("--template-spec-root", type=Path, required=True)
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser("generate")
    generate.add_argument("--project-id", required=True)
    generate.add_argument("--generation-run-id", required=True)

    publish = subparsers.add_parser("publish")
    publish.add_argument("--upload-job-id", required=True)

    args = parser.parse_args()

    if args.command == "generate":
        run_generation_job(args.db_path, args.storage_root, args.template_spec_root, args.project_id, args.generation_run_id)
        return

    if args.command == "publish":
        run_publish_job(args.db_path, args.storage_root, args.template_spec_root, args.upload_job_id)


if __name__ == "__main__":
    main()

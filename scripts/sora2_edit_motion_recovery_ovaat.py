from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from services.common.env_loader import load_repo_env
from video_benchmark_common import create_contact_sheet, extract_video_frames, image_metrics, video_motion_metrics


SOURCE_SUMMARY_PATH = (
    REPO_ROOT
    / "docs"
    / "experiments"
    / "artifacts"
    / "exp-92-sora2-input-framing-ovaat"
    / "hero_tight_zoom"
    / "맥주"
    / "summary.json"
)
BASELINE_SUMMARY_PATH = (
    REPO_ROOT
    / "docs"
    / "experiments"
    / "artifacts"
    / "exp-90-upper-bound-video-benchmark"
    / "sora2"
    / "맥주"
    / "summary.json"
)
MANUAL_VEO_SUMMARY_PATH = (
    REPO_ROOT
    / "docs"
    / "experiments"
    / "artifacts"
    / "exp-90-upper-bound-video-benchmark"
    / "manual_veo"
    / "맥주"
    / "summary.json"
)
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-93-sora2-edit-motion-recovery-ovaat"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def extract_video_id(payload: dict[str, object]) -> str:
    for key in ("id", "video_id"):
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
    nested_video = payload.get("video")
    if isinstance(nested_video, dict):
        value = nested_video.get("id")
        if isinstance(value, str) and value:
            return value
    raise ValueError("edit response에서 video id를 찾지 못했습니다.")


def read_reference(summary_path: Path, *, variant_name: str, provider: str) -> dict[str, object]:
    summary = read_json(summary_path)
    motion_metrics = summary.get("motion_metrics")
    output_video = summary.get("output_video")
    if motion_metrics is None and output_video:
        motion_metrics = video_motion_metrics(Path(str(output_video)))
    return {
        "provider": provider,
        "variant": variant_name,
        "status": summary.get("status"),
        "summary_path": str(summary_path),
        "video_id": summary.get("video_id"),
        "output_video": output_video,
        "output_mid_frame": summary.get("output_mid_frame"),
        "contact_sheet": summary.get("contact_sheet"),
        "prompt": summary.get("prompt"),
        "mid_frame_metrics": summary.get("mid_frame_metrics"),
        "motion_metrics": motion_metrics,
        "resolved_prepare_mode": summary.get("resolved_prepare_mode"),
    }


def compare_to_source(result: dict[str, object], source: dict[str, object]) -> dict[str, float | None]:
    source_mid = source.get("mid_frame_metrics") or {}
    source_motion = source.get("motion_metrics") or {}
    result_mid = result.get("mid_frame_metrics") or {}
    result_motion = result.get("motion_metrics") or {}

    def diff(current: object, base: object) -> float | None:
        if current is None or base is None:
            return None
        return round(float(current) - float(base), 2)

    return {
        "mid_frame_mse_delta": diff(result_mid.get("mse"), source_mid.get("mse")),
        "avg_rgb_diff_delta": diff(result_motion.get("avg_rgb_diff"), source_motion.get("avg_rgb_diff")),
        "avg_gray_diff_delta": diff(result_motion.get("avg_gray_diff"), source_motion.get("avg_gray_diff")),
    }


def edit_prompt_variants() -> dict[str, str]:
    return {
        "same_shot_more_motion": (
            "Same shot and framing. Keep the bottle position, label readability, glass position, tabletop pattern, "
            "and background unchanged. Increase visible beverage motion only: continuous bubbles rising through the beer, "
            "foam settling over 4 seconds, condensation highlights sliding across the glass, and a very small camera drift. "
            "No new objects, no duplicated bottle or glass, no shape changes."
        ),
        "same_shot_push_in_motion": (
            "Same shot and framing. Keep the bottle position, label, glass shape, tabletop pattern, and background unchanged. "
            "Make the motion more visible with a slow controlled push-in, a slight rightward camera drift, bubble streams in the beer, "
            "and a gentle foam movement. Preserve the original composition and product identity. No new objects, no label rewrite, no shape changes."
        ),
    }


def run_edit_variant(
    *,
    source_video_id: str,
    source_prepared_input: Path,
    variant_name: str,
    prompt: str,
    output_dir: Path,
) -> dict[str, object]:
    variant_dir = output_dir / variant_name
    variant_dir.mkdir(parents=True, exist_ok=True)
    edit_json = variant_dir / "edit.json"
    poll_json = variant_dir / "poll.json"
    output_video = variant_dir / "edit_result.mp4"
    summary_path = variant_dir / "summary.json"
    artifact: dict[str, object] = {
        "provider": "sora2_edit",
        "variant": variant_name,
        "source_video_id": source_video_id,
        "source_prepared_input": str(source_prepared_input),
        "prompt": prompt,
    }
    try:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("openai 패키지가 필요합니다. `uv run --with openai ...` 형태로 실행해 주세요.") from exc

        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY가 설정되어 있지 않습니다.")

        client = OpenAI(api_key=api_key)
        edit_payload = client.post(
            "/videos/edits",
            cast_to=dict[str, object],
            body={"prompt": prompt, "video": {"id": source_video_id}},
        )
        write_json(edit_json, edit_payload)
        edit_video_id = extract_video_id(edit_payload)
        artifact["edit_video_id"] = edit_video_id

        started_at = time.perf_counter()
        while True:
            final_payload = client.get(f"/videos/{edit_video_id}", cast_to=dict[str, object])
            status = str(final_payload.get("status") or "unknown")
            if status in {"completed", "failed", "cancelled"}:
                break
            if (time.perf_counter() - started_at) > 900:
                raise TimeoutError(f"{variant_name} edit polling timed out.")
            time.sleep(10)

        write_json(poll_json, final_payload)
        artifact["final_status"] = status
        artifact["final_payload_path"] = str(poll_json)
        if status != "completed":
            artifact["status"] = "failed"
            artifact["error_stage"] = "poll"
            artifact["error"] = final_payload.get("error")
            write_json(summary_path, artifact)
            return artifact

        content = client.videos.download_content(edit_video_id)
        content.write_to_file(output_video)
        first_frame_path, mid_frame_path = extract_video_frames(output_video, variant_dir, midpoint_seconds=2.0)
        contact_sheet_path = create_contact_sheet(output_video, variant_dir / "contact_sheet.png")
        artifact.update(
            {
                "status": "completed",
                "output_video": str(output_video),
                "output_first_frame": str(first_frame_path),
                "output_mid_frame": str(mid_frame_path),
                "contact_sheet": str(contact_sheet_path),
                "first_frame_metrics": image_metrics(source_prepared_input, first_frame_path),
                "mid_frame_metrics": image_metrics(source_prepared_input, mid_frame_path),
                "motion_metrics": video_motion_metrics(output_video),
            }
        )
    except Exception as exc:
        artifact["status"] = "failed"
        artifact["error_type"] = exc.__class__.__name__
        artifact["error"] = str(exc)

    write_json(summary_path, artifact)
    artifact["summary_path"] = str(summary_path)
    return artifact


def main() -> None:
    load_repo_env()
    parser = argparse.ArgumentParser(description="Run Sora edit-based motion recovery OVAT from the hero_tight source video.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    source_summary = read_json(SOURCE_SUMMARY_PATH)
    source_reference = read_reference(SOURCE_SUMMARY_PATH, variant_name="source_hero_tight", provider="sora2")
    baseline_reference = read_reference(BASELINE_SUMMARY_PATH, variant_name="baseline_reused", provider="sora2")
    manual_veo_reference = read_reference(MANUAL_VEO_SUMMARY_PATH, variant_name="manual_veo_reference", provider="manual_veo")
    source_video_id = str(source_summary["video_id"])
    source_prepared_input = Path(str(source_summary["prepared_input"]))

    variants: dict[str, object] = {
        "source_hero_tight": source_reference,
        "baseline_reused": baseline_reference,
        "manual_veo_reference": manual_veo_reference,
    }

    for variant_name, prompt in edit_prompt_variants().items():
        result = run_edit_variant(
            source_video_id=source_video_id,
            source_prepared_input=source_prepared_input,
            variant_name=variant_name,
            prompt=prompt,
            output_dir=args.output_dir,
        )
        if result.get("status") == "completed":
            result["source_comparison"] = compare_to_source(result, source_reference)
        variants[variant_name] = result

    summary = {
        "experiment_id": "EXP-93-sora2-edit-motion-recovery-ovaat",
        "source_summary": str(SOURCE_SUMMARY_PATH),
        "variants": variants,
    }
    write_json(args.output_dir / "summary.json", summary)
    print(args.output_dir / "summary.json")


if __name__ == "__main__":
    main()

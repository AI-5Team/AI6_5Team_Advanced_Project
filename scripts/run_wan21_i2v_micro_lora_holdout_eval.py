from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import torch
from diffusers import AutoencoderKLWan, WanImageToVideoPipeline, WanTransformer3DModel
from diffusers.hooks.group_offloading import apply_group_offloading
from diffusers.utils import export_to_video
from PIL import Image
from transformers import CLIPVisionModel, UMT5EncoderModel


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.common.env_loader import load_repo_env
from services.worker.renderers.framing import choose_prepare_mode, prepare_image
from scripts.video_benchmark_common import create_contact_sheet, image_metrics, video_motion_metrics, write_json


DEFAULT_MANIFEST = (
    REPO_ROOT
    / "docs"
    / "experiments"
    / "artifacts"
    / "exp-265-wan21-i2v-micro-lora-dataset-prep"
    / "manifest.json"
)
DEFAULT_OUTPUT_DIR = (
    REPO_ROOT
    / "docs"
    / "experiments"
    / "artifacts"
    / "exp-267-wan21-i2v-micro-lora-holdout-delta-check"
)
DEFAULT_MODEL_ID = "Wan-AI/Wan2.1-I2V-14B-480P-Diffusers"
DEFAULT_LORA_VARIANTS = {
    "step001": REPO_ROOT
    / "docs"
    / "experiments"
    / "artifacts"
    / "exp-266-wan21-i2v-micro-lora-dry-run"
    / "run_steps_001"
    / "lora_weights"
    / "000001",
    "step002": REPO_ROOT
    / "docs"
    / "experiments"
    / "artifacts"
    / "exp-266-wan21-i2v-micro-lora-dry-run"
    / "run_steps_002"
    / "lora_weights"
    / "000002",
}


def _gpu_info() -> dict[str, object]:
    info: dict[str, object] = {
        "cuda_available": torch.cuda.is_available(),
        "device_name": None,
        "bf16_supported": None,
        "free_vram_gb": None,
        "total_vram_gb": None,
    }
    if torch.cuda.is_available():
        info["device_name"] = torch.cuda.get_device_name(0)
        info["bf16_supported"] = torch.cuda.is_bf16_supported()
        free_mem, total_mem = torch.cuda.mem_get_info(0)
        info["free_vram_gb"] = round(free_mem / 1024**3, 2)
        info["total_vram_gb"] = round(total_mem / 1024**3, 2)
    return info


def _step_logger(label: str):
    def _callback(pipe, step_index, timestep, callback_kwargs):
        print(f"[{label}] step={step_index + 1} timestep={timestep}", flush=True)
        return callback_kwargs

    return _callback


def _load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_eval_samples(manifest: dict, labels: list[str] | None) -> list[dict]:
    eval_samples = list(manifest.get("evalSamples") or [])
    if not labels:
        return eval_samples
    label_set = set(labels)
    return [sample for sample in eval_samples if sample["label"] in label_set]


def _load_pipeline(model_id: str) -> WanImageToVideoPipeline:
    image_encoder = CLIPVisionModel.from_pretrained(model_id, subfolder="image_encoder", torch_dtype=torch.float32)
    text_encoder = UMT5EncoderModel.from_pretrained(model_id, subfolder="text_encoder", torch_dtype=torch.bfloat16)
    vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float32)
    transformer = WanTransformer3DModel.from_pretrained(model_id, subfolder="transformer", torch_dtype=torch.bfloat16)

    onload_device = torch.device("cuda")
    offload_device = torch.device("cpu")
    apply_group_offloading(
        text_encoder,
        onload_device=onload_device,
        offload_device=offload_device,
        offload_type="block_level",
        num_blocks_per_group=4,
    )
    transformer.enable_group_offload(
        onload_device=onload_device,
        offload_device=offload_device,
        offload_type="block_level",
        num_blocks_per_group=4,
    )

    pipe = WanImageToVideoPipeline.from_pretrained(
        model_id,
        vae=vae,
        transformer=transformer,
        text_encoder=text_encoder,
        image_encoder=image_encoder,
        torch_dtype=torch.bfloat16,
    )
    pipe.to("cuda")
    return pipe


def _apply_variant(pipe: WanImageToVideoPipeline, variant_name: str) -> None:
    try:
        pipe.unload_lora_weights()
    except Exception:
        pass

    if variant_name == "base":
        return

    lora_path = DEFAULT_LORA_VARIANTS[variant_name]
    pipe.load_lora_weights(str(lora_path), adapter_name=variant_name)
    pipe.set_adapters(variant_name, 1.0)


def _save_run_outputs(
    *,
    frames,
    output_dir: Path,
    fps: int,
    prepared_input_path: Path,
    elapsed_seconds: float,
    sample: dict,
    variant_name: str,
    run_config: dict[str, object],
) -> dict[str, object]:
    normalized_frames: list[Image.Image] = []
    for frame in frames:
        if isinstance(frame, Image.Image):
            normalized_frames.append(frame)
        else:
            normalized_frames.append(Image.fromarray(frame))

    video_path = output_dir / "wan21_output.mp4"
    first_frame_path = output_dir / "first_frame.png"
    mid_frame_path = output_dir / "mid_frame.png"
    contact_sheet_path = output_dir / "contact_sheet.png"
    export_to_video(normalized_frames, str(video_path), fps=fps)
    normalized_frames[0].save(first_frame_path)
    normalized_frames[len(normalized_frames) // 2].save(mid_frame_path)
    create_contact_sheet(video_path, contact_sheet_path)

    artifact = {
        "status": "completed",
        "label": sample["label"],
        "variant": variant_name,
        "imagePath": sample["imagePath"],
        "caption": sample["caption"],
        "preparedInputPath": str(prepared_input_path),
        "outputVideoPath": str(video_path),
        "outputFirstFramePath": str(first_frame_path),
        "outputMidFramePath": str(mid_frame_path),
        "outputContactSheetPath": str(contact_sheet_path),
        "elapsedSeconds": round(elapsed_seconds, 2),
        "frameCount": len(normalized_frames),
        "firstFrameMetrics": image_metrics(prepared_input_path, first_frame_path),
        "midFrameMetrics": image_metrics(prepared_input_path, mid_frame_path),
        "motionMetrics": video_motion_metrics(video_path),
        "runConfig": run_config,
    }
    write_json(output_dir / "summary.json", artifact)
    return artifact


def main() -> None:
    load_repo_env()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Run held-out base vs micro-LoRA delta check for Wan 2.1 I2V 480P.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--labels", nargs="*", default=None)
    parser.add_argument("--variants", nargs="*", default=["base", "step001", "step002"])
    parser.add_argument("--num-frames", type=int, default=13)
    parser.add_argument("--fps", type=int, default=8)
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--guidance-scale", type=float, default=5.0)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    manifest = _load_manifest(args.manifest)
    eval_samples = _resolve_eval_samples(manifest, args.labels)
    if not eval_samples:
        raise ValueError("no eval samples selected")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    pipe = _load_pipeline(DEFAULT_MODEL_ID)

    aggregate_results: list[dict[str, object]] = []
    try:
        for sample in eval_samples:
            image_path = Path(str(sample["imagePath"]))
            prepare_mode = choose_prepare_mode(image_path)
            prepared = prepare_image(image_path, 832, 480, prepare_mode)

            for variant_name in args.variants:
                if variant_name != "base" and variant_name not in DEFAULT_LORA_VARIANTS:
                    raise ValueError(f"unknown variant: {variant_name}")

                _apply_variant(pipe, variant_name)
                run_dir = args.output_dir / sample["label"] / variant_name
                run_dir.mkdir(parents=True, exist_ok=True)
                prepared_input_path = run_dir / "prepared_input.png"
                prepared.save(prepared_input_path)

                run_config = {
                    "modelId": DEFAULT_MODEL_ID,
                    "variant": variant_name,
                    "prepareMode": prepare_mode,
                    "width": 832,
                    "height": 480,
                    "numFrames": args.num_frames,
                    "fps": args.fps,
                    "numInferenceSteps": args.steps,
                    "guidanceScale": args.guidance_scale,
                    "seed": args.seed,
                    "gpu": _gpu_info(),
                }

                print(
                    json.dumps({"label": sample["label"], "variant": variant_name, "status": "started"}, ensure_ascii=False),
                    flush=True,
                )
                started = time.perf_counter()
                result = pipe(
                    image=prepared,
                    prompt=sample["caption"],
                    negative_prompt=(
                        "Bright tones, overexposed, static, blurred details, subtitles, style, works, paintings, images, static, "
                        "overall gray, worst quality, low quality, JPEG compression residue, ugly, incomplete, extra fingers, "
                        "poorly drawn hands, poorly drawn faces, deformed, disfigured, misshapen limbs, fused fingers, still picture, "
                        "messy background, three legs, many people in the background, walking backwards"
                    ),
                    height=480,
                    width=832,
                    num_frames=args.num_frames,
                    num_inference_steps=args.steps,
                    guidance_scale=args.guidance_scale,
                    generator=torch.Generator(device="cpu").manual_seed(args.seed),
                    callback_on_step_end=_step_logger(f"{sample['label']}/{variant_name}"),
                )
                artifact = _save_run_outputs(
                    frames=result.frames[0],
                    output_dir=run_dir,
                    fps=args.fps,
                    prepared_input_path=prepared_input_path,
                    elapsed_seconds=time.perf_counter() - started,
                    sample=sample,
                    variant_name=variant_name,
                    run_config=run_config,
                )
                aggregate_results.append(artifact)
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

    finally:
        try:
            pipe.unload_lora_weights()
        except Exception:
            pass
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    comparison: dict[str, dict[str, object]] = {}
    for sample in eval_samples:
        label = sample["label"]
        sample_results = [item for item in aggregate_results if item["label"] == label]
        base = next((item for item in sample_results if item["variant"] == "base"), None)
        variants = []
        for item in sample_results:
            if item["variant"] == "base" or base is None:
                continue
            variants.append(
                {
                    "variant": item["variant"],
                    "firstFrameMseDeltaVsBase": round(item["firstFrameMetrics"]["mse"] - base["firstFrameMetrics"]["mse"], 2),
                    "midFrameMseDeltaVsBase": round(item["midFrameMetrics"]["mse"] - base["midFrameMetrics"]["mse"], 2),
                    "motionAvgRgbDeltaVsBase": round(
                        item["motionMetrics"]["avg_rgb_diff"] - base["motionMetrics"]["avg_rgb_diff"], 2
                    ),
                    "elapsedSecondsDeltaVsBase": round(item["elapsedSeconds"] - base["elapsedSeconds"], 2),
                }
            )
        comparison[label] = {
            "base": base,
            "variants": variants,
        }

    report = {
        "manifestPath": str(args.manifest),
        "outputDir": str(args.output_dir),
        "labels": [sample["label"] for sample in eval_samples],
        "variants": args.variants,
        "aggregateResults": aggregate_results,
        "comparison": comparison,
    }
    write_json(args.output_dir / "comparison_summary.json", report)
    print(args.output_dir / "comparison_summary.json", flush=True)


if __name__ == "__main__":
    main()

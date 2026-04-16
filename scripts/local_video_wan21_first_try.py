from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch
from diffusers import (
    AutoencoderKLWan,
    UniPCMultistepScheduler,
    WanImageToVideoPipeline,
    WanPipeline,
    WanTransformer3DModel,
    WanVACEPipeline,
)
from diffusers.hooks.group_offloading import apply_group_offloading
from diffusers.utils import export_to_video
from PIL import Image
from transformers import CLIPVisionModel, UMT5EncoderModel


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.common.env_loader import load_repo_env
from services.worker.renderers.framing import choose_prepare_mode, prepare_image
from scripts.video_benchmark_common import (
    build_upper_bound_prompt,
    create_contact_sheet,
    extract_video_frames,
    image_metrics,
    infer_label,
    video_motion_metrics,
    write_json,
)


DEFAULT_IMAGE = REPO_ROOT / "docs" / "sample" / "음식사진샘플(규카츠).jpg"
DEFAULT_NEGATIVE_PROMPT = (
    "Bright tones, overexposed, static, blurred details, subtitles, style, works, paintings, images, static, "
    "overall gray, worst quality, low quality, JPEG compression residue, ugly, incomplete, extra fingers, poorly "
    "drawn hands, poorly drawn faces, deformed, disfigured, misshapen limbs, fused fingers, still picture, messy "
    "background, three legs, many people in the background, walking backwards"
)


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


def _target_area(resolution_tier: int) -> int:
    if resolution_tier == 720:
        return 720 * 832
    if resolution_tier == 480:
        return 480 * 832
    raise ValueError(f"unsupported resolution tier: {resolution_tier}")


def _resolve_dimensions(
    *,
    patch_multiple: int,
    target_area: int,
    aspect_ratio: float,
) -> tuple[int, int]:
    height = round(math.sqrt(target_area * aspect_ratio))
    width = round(math.sqrt(target_area / aspect_ratio))
    height = max(patch_multiple, height // patch_multiple * patch_multiple)
    width = max(patch_multiple, width // patch_multiple * patch_multiple)
    return height, width


def _prepare_video_and_mask(image: Image.Image, height: int, width: int, num_frames: int):
    first_img = image.resize((width, height))
    last_img = image.resize((width, height))
    frames = [first_img]
    frames.extend([Image.new("RGB", (width, height), (128, 128, 128))] * (num_frames - 2))
    frames.append(last_img)
    mask_black = Image.new("L", (width, height), 0)
    mask_white = Image.new("L", (width, height), 255)
    mask = [mask_black, *[mask_white] * (num_frames - 2), mask_black]
    return frames, mask


def _prompt_for_mode(image_path: Path, mode: str) -> str:
    base = build_upper_bound_prompt(image_path)
    label = infer_label(image_path)
    if mode == "t2v":
        return (
            f"Vertical food commercial short for {label}. "
            f"{base} Keep the scene readable as an ad with a clear hero subject and restrained camera motion."
        )
    if mode == "vace":
        return (
            f"Preserve the input food photo of {label}. "
            f"{base} Animate only subtle ad-friendly motion while keeping the dish layout and brand-safe composition."
        )
    return base


def _save_outputs(
    *,
    frames,
    output_dir: Path,
    fps: int,
    prepared_input_path: Path | None,
    elapsed_seconds: float,
    artifact: dict[str, object],
) -> dict[str, object]:
    normalized_frames = []
    for frame in frames:
        if isinstance(frame, Image.Image):
            normalized_frames.append(frame)
            continue
        array = np.asarray(frame)
        if array.dtype != np.uint8:
            if array.max() <= 1.0:
                array = (array * 255.0).clip(0, 255).astype(np.uint8)
            else:
                array = array.clip(0, 255).astype(np.uint8)
        normalized_frames.append(Image.fromarray(array))
    video_path = output_dir / "wan21_output.mp4"
    first_frame_path = output_dir / "first_frame.png"
    mid_frame_path = output_dir / "mid_frame.png"
    contact_sheet_path = output_dir / "contact_sheet.png"
    export_to_video(normalized_frames, str(video_path), fps=fps)
    normalized_frames[0].save(first_frame_path)
    normalized_frames[len(normalized_frames) // 2].save(mid_frame_path)
    create_contact_sheet(video_path, contact_sheet_path)

    artifact.update(
        {
            "status": "completed",
            "frame_count": len(normalized_frames),
            "elapsed_seconds": round(elapsed_seconds, 2),
            "output_video": str(video_path),
            "output_first_frame": str(first_frame_path),
            "output_mid_frame": str(mid_frame_path),
            "output_contact_sheet": str(contact_sheet_path),
            "motion_metrics": video_motion_metrics(video_path),
        }
    )
    if prepared_input_path is not None:
        artifact["prepared_input"] = str(prepared_input_path)
        artifact["first_frame_metrics"] = image_metrics(prepared_input_path, first_frame_path)
        artifact["mid_frame_metrics"] = image_metrics(prepared_input_path, mid_frame_path)
    return artifact


def _step_logger(label: str):
    def _callback(pipe, step_index, timestep, callback_kwargs):
        print(f"[{label}] step={step_index + 1} timestep={timestep}")
        return callback_kwargs

    return _callback


def _run_vace(args, output_dir: Path) -> dict[str, object]:
    model_id = "Wan-AI/Wan2.1-VACE-1.3B-diffusers"
    gpu = _gpu_info()
    prepared = prepare_image(args.image, args.width, args.height, choose_prepare_mode(args.image))
    prepared_path = output_dir / "prepared_input.png"
    prepared.save(prepared_path)

    started = time.perf_counter()
    artifact: dict[str, object] = {
        "mode": "vace",
        "model_id": model_id,
        "resolution_tier": args.resolution_tier,
        "width": args.width,
        "height": args.height,
        "num_frames": args.num_frames,
        "num_inference_steps": args.steps,
        "guidance_scale": args.guidance_scale,
        "seed": args.seed,
        "gpu": gpu,
        "prompt": args.prompt,
    }

    vae = AutoencoderKLWan.from_pretrained(model_id, subfolder="vae", torch_dtype=torch.float32)
    pipe = WanVACEPipeline.from_pretrained(model_id, vae=vae, torch_dtype=torch.bfloat16)
    flow_shift = 5.0 if args.resolution_tier == 720 else 3.0
    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config, flow_shift=flow_shift)
    pipe.to("cuda")

    conditioning_video, conditioning_mask = _prepare_video_and_mask(prepared, args.height, args.width, args.num_frames)
    generator = torch.Generator(device="cpu").manual_seed(args.seed)
    result = pipe(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        video=conditioning_video,
        mask=conditioning_mask,
        reference_images=[prepared],
        conditioning_scale=1.0,
        height=args.height,
        width=args.width,
        num_frames=args.num_frames,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance_scale,
        generator=generator,
        callback_on_step_end=_step_logger("vace"),
    )
    return _save_outputs(
        frames=result.frames[0],
        output_dir=output_dir,
        fps=args.fps,
        prepared_input_path=prepared_path,
        elapsed_seconds=time.perf_counter() - started,
        artifact=artifact,
    )


def _run_t2v(args, output_dir: Path) -> dict[str, object]:
    model_id = "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
    gpu = _gpu_info()
    prepared = prepare_image(args.image, args.width, args.height, choose_prepare_mode(args.image))
    prepared_path = output_dir / "prepared_input.png"
    prepared.save(prepared_path)

    started = time.perf_counter()
    artifact: dict[str, object] = {
        "mode": "t2v",
        "model_id": model_id,
        "resolution_tier": args.resolution_tier,
        "width": args.width,
        "height": args.height,
        "num_frames": args.num_frames,
        "num_inference_steps": args.steps,
        "guidance_scale": args.guidance_scale,
        "seed": args.seed,
        "gpu": gpu,
        "prompt": args.prompt,
    }

    pipe = WanPipeline.from_pretrained(model_id, torch_dtype=torch.bfloat16)
    pipe.to("cuda")
    generator = torch.Generator(device="cpu").manual_seed(args.seed)
    result = pipe(
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        height=args.height,
        width=args.width,
        num_frames=args.num_frames,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance_scale,
        generator=generator,
        callback_on_step_end=_step_logger("t2v"),
    )
    return _save_outputs(
        frames=result.frames[0],
        output_dir=output_dir,
        fps=args.fps,
        prepared_input_path=prepared_path,
        elapsed_seconds=time.perf_counter() - started,
        artifact=artifact,
    )


def _run_i2v(args, output_dir: Path) -> dict[str, object]:
    model_id = "Wan-AI/Wan2.1-I2V-14B-720P-Diffusers"
    gpu = _gpu_info()
    prepared = prepare_image(args.image, args.width, args.height, choose_prepare_mode(args.image))
    prepared_path = output_dir / "prepared_input.png"
    prepared.save(prepared_path)

    started = time.perf_counter()
    artifact: dict[str, object] = {
        "mode": "i2v",
        "model_id": model_id,
        "resolution_tier": args.resolution_tier,
        "width": args.width,
        "height": args.height,
        "num_frames": args.num_frames,
        "num_inference_steps": args.steps,
        "guidance_scale": args.guidance_scale,
        "seed": args.seed,
        "gpu": gpu,
        "prompt": args.prompt,
        "offload_mode": "group_offloading",
    }

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
    generator = torch.Generator(device="cpu").manual_seed(args.seed)
    result = pipe(
        image=prepared,
        prompt=args.prompt,
        negative_prompt=args.negative_prompt,
        height=args.height,
        width=args.width,
        num_frames=args.num_frames,
        num_inference_steps=args.steps,
        guidance_scale=args.guidance_scale,
        generator=generator,
        callback_on_step_end=_step_logger("i2v"),
    )
    return _save_outputs(
        frames=result.frames[0],
        output_dir=output_dir,
        fps=args.fps,
        prepared_input_path=prepared_path,
        elapsed_seconds=time.perf_counter() - started,
        artifact=artifact,
    )


def main() -> None:
    load_repo_env()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Run Wan 2.1 local video feasibility checks.")
    parser.add_argument("--mode", choices=["vace", "t2v", "i2v"], required=True)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--resolution-tier", type=int, choices=[480, 720], default=720)
    parser.add_argument("--target-aspect", choices=["9:16", "16:9", "source"], default="9:16")
    parser.add_argument("--num-frames", type=int, default=33)
    parser.add_argument("--fps", type=int, default=16)
    parser.add_argument("--steps", type=int, default=18)
    parser.add_argument("--guidance-scale", type=float, default=5.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--negative-prompt", default=DEFAULT_NEGATIVE_PROMPT)
    parser.add_argument("--prompt", default=None)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    patch_multiple = 32
    if args.target_aspect == "9:16":
        aspect_ratio = 16 / 9
    elif args.target_aspect == "16:9":
        aspect_ratio = 9 / 16
    else:
        image = Image.open(args.image)
        aspect_ratio = image.height / image.width
    height, width = _resolve_dimensions(
        patch_multiple=patch_multiple,
        target_area=_target_area(args.resolution_tier),
        aspect_ratio=aspect_ratio,
    )
    args.height = height
    args.width = width
    args.prompt = args.prompt or _prompt_for_mode(args.image, args.mode)
    summary_path = args.output_dir / "summary.json"

    try:
        if args.mode == "vace":
            artifact = _run_vace(args, args.output_dir)
        elif args.mode == "t2v":
            artifact = _run_t2v(args, args.output_dir)
        else:
            artifact = _run_i2v(args, args.output_dir)
    except Exception as exc:
        artifact = {
            "mode": args.mode,
            "image": str(args.image),
            "resolution_tier": args.resolution_tier,
            "width": args.width,
            "height": args.height,
            "num_frames": args.num_frames,
            "num_inference_steps": args.steps,
            "guidance_scale": args.guidance_scale,
            "seed": args.seed,
            "gpu": _gpu_info(),
            "prompt": args.prompt,
            "status": "failed",
            "error_type": exc.__class__.__name__,
            "error": str(exc),
        }
    finally:
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

    write_json(summary_path, artifact)
    print(json.dumps(artifact, ensure_ascii=False, indent=2))
    print(f"artifact_path={summary_path}")


if __name__ == "__main__":
    main()

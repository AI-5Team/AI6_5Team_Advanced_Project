from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import torch
from diffusers import CogVideoXImageToVideoPipeline
from diffusers.utils import export_to_video
from PIL import Image, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.common.env_loader import load_repo_env


DEFAULT_IMAGE = REPO_ROOT / "docs" / "sample" / "음식사진샘플(규카츠).jpg"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-38-local-cogvideox-first-try"
DEFAULT_NEGATIVE_PROMPT = "blurry, jittery, deformed, duplicated, inconsistent motion, low quality, watermark, text"


def build_prompt_from_filename(image_path: Path) -> str:
    stem = image_path.stem
    if "규카츠" in stem:
        return (
            "A close-up food commercial shot of crispy gyukatsu on a tray, "
            "gentle steam rising, subtle camera push-in, warm restaurant lighting, "
            "realistic texture, cinematic but natural motion"
        )
    if "라멘" in stem:
        return (
            "A close-up food commercial shot of ramen, broth shimmering softly, "
            "gentle steam, slight camera push-in, warm restaurant lighting, realistic motion"
        )
    return (
        "A close-up food commercial shot of plated food, gentle steam, "
        "warm restaurant lighting, realistic motion"
    )


def prepare_image(image_path: Path, width: int, height: int) -> Image.Image:
    image = Image.open(image_path).convert("RGB")
    return ImageOps.fit(image, (width, height), method=Image.Resampling.LANCZOS)


def main() -> None:
    load_repo_env()
    parser = argparse.ArgumentParser(description="Run a first local CogVideoX I2V attempt.")
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--model", default="THUDM/CogVideoX-5b-I2V")
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--num-frames", type=int, default=16)
    parser.add_argument("--fps", type=int, default=8)
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--guidance-scale", type=float, default=6.0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--prompt", default=None)
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_video_path = args.output_dir / "cogvideox_first_try.mp4"
    output_frame_path = args.output_dir / "cogvideox_first_try_first_frame.png"
    output_mid_frame_path = args.output_dir / "cogvideox_first_try_mid_frame.png"
    prepared_input_path = args.output_dir / "prepared_input.png"
    artifact_path = args.output_dir / "summary.json"

    prompt = args.prompt or build_prompt_from_filename(args.image)
    image = prepare_image(args.image, args.width, args.height)
    image.save(prepared_input_path)

    artifact: dict[str, object] = {
        "image": str(args.image),
        "prepared_input": str(prepared_input_path),
        "model": args.model,
        "prompt": prompt,
        "negative_prompt": DEFAULT_NEGATIVE_PROMPT,
        "width": args.width,
        "height": args.height,
        "num_frames": args.num_frames,
        "fps": args.fps,
        "steps": args.steps,
        "guidance_scale": args.guidance_scale,
        "seed": args.seed,
        "python": sys.version,
        "torch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
        "bf16_supported": torch.cuda.is_bf16_supported() if torch.cuda.is_available() else None,
        "status": "started",
        "output_video": str(output_video_path),
        "output_first_frame": str(output_frame_path),
        "output_mid_frame": str(output_mid_frame_path),
    }

    started_at = time.perf_counter()
    try:
        pipe = CogVideoXImageToVideoPipeline.from_pretrained(
            args.model,
            torch_dtype=torch.bfloat16,
        )
        if hasattr(pipe.vae, "enable_slicing"):
            pipe.vae.enable_slicing()
        if hasattr(pipe.vae, "enable_tiling"):
            pipe.vae.enable_tiling()
        pipe.enable_model_cpu_offload()

        generator = torch.Generator(device="cpu").manual_seed(args.seed)
        result = pipe(
            image=image,
            prompt=prompt,
            negative_prompt=DEFAULT_NEGATIVE_PROMPT,
            height=args.height,
            width=args.width,
            num_frames=args.num_frames,
            num_inference_steps=args.steps,
            guidance_scale=args.guidance_scale,
            use_dynamic_cfg=True,
            generator=generator,
        )
        frames = result.frames[0]
        frames[0].save(output_frame_path)
        frames[len(frames) // 2].save(output_mid_frame_path)
        export_to_video(frames, str(output_video_path), fps=args.fps)

        artifact["status"] = "completed"
        artifact["frame_count"] = len(frames)
    except Exception as exc:
        artifact["status"] = "failed"
        artifact["error_type"] = exc.__class__.__name__
        artifact["error"] = str(exc)
    finally:
        artifact["elapsed_seconds"] = round(time.perf_counter() - started_at, 2)
        artifact_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps(artifact, ensure_ascii=False, indent=2))
        print(f"artifact_path={artifact_path}")


if __name__ == "__main__":
    main()

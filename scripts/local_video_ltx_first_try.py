from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import torch
from diffusers import GGUFQuantizationConfig, LTXImageToVideoPipeline, LTXVideoTransformer3DModel
from diffusers.utils import export_to_video
from huggingface_hub import hf_hub_download
from PIL import Image, ImageFilter, ImageOps


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.common.env_loader import load_repo_env
from scripts.local_video_ltx_prepare_mode_classifier import classify_shot_type, choose_prepare_mode, extract_structure_features


DEFAULT_IMAGE = REPO_ROOT / "docs" / "sample" / "음식사진샘플(규카츠).jpg"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "docs" / "experiments" / "artifacts" / "exp-36-local-ltx-video-first-try"
DEFAULT_NEGATIVE_PROMPT = "worst quality, blurry, jittery, distorted, warped, overexposed, text, watermark"


def build_prompt_from_filename(image_path: Path) -> str:
    stem = image_path.stem
    if "규카츠" in stem:
        return (
            "Close-up of crispy gyukatsu on a plate, steam rising softly, "
            "golden cutlet texture clearly visible, camera slowly pushes in, "
            "warm izakaya lighting, realistic food commercial motion"
        )
    if "라멘" in stem:
        return (
            "Close-up of ramen bowl with rich broth and noodles, light steam rising, "
            "camera slowly tilts and pushes in, cozy restaurant lighting, realistic food commercial motion"
        )
    return (
        "Close-up of plated food, subtle steam, gentle camera push in, "
        "warm restaurant lighting, realistic food commercial motion"
    )


def _prepare_cover(image: Image.Image, width: int, height: int, centering: tuple[float, float] = (0.5, 0.5)) -> Image.Image:
    return ImageOps.fit(image, (width, height), method=Image.Resampling.LANCZOS, centering=centering)


def _prepare_contain_blur(image: Image.Image, width: int, height: int) -> Image.Image:
    contained = ImageOps.contain(image, (width, height), method=Image.Resampling.LANCZOS)
    background = image.resize((width, height), Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(radius=24))
    offset = ((width - contained.width) // 2, (height - contained.height) // 2)
    background.paste(contained, offset)
    return background


def prepare_image(image_path: Path, width: int, height: int, prepare_mode: str) -> Image.Image:
    image = Image.open(image_path).convert("RGB")
    if prepare_mode == "cover_center":
        return _prepare_cover(image, width, height, centering=(0.5, 0.5))
    if prepare_mode == "cover_top":
        return _prepare_cover(image, width, height, centering=(0.5, 0.35))
    if prepare_mode == "cover_bottom":
        return _prepare_cover(image, width, height, centering=(0.5, 0.7))
    if prepare_mode == "contain_blur":
        return _prepare_contain_blur(image, width, height)
    raise ValueError(f"unsupported prepare mode: {prepare_mode}")


def main() -> None:
    load_repo_env()
    parser = argparse.ArgumentParser(description="Run a first local LTX-Video 2B / GGUF image-to-video attempt.")
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE, help="Source image path.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory for mp4/png/json outputs.")
    parser.add_argument("--base-repo", default="Lightricks/LTX-Video", help="Base diffusers repo.")
    parser.add_argument("--gguf-repo", default="city96/LTX-Video-gguf", help="GGUF model repo id.")
    parser.add_argument("--gguf-file", default="ltx-video-2b-v0.9-Q3_K_S.gguf", help="GGUF file name inside the repo.")
    parser.add_argument("--width", type=int, default=704)
    parser.add_argument("--height", type=int, default=480)
    parser.add_argument("--num-frames", type=int, default=25)
    parser.add_argument("--fps", type=int, default=12)
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--guidance-scale", type=float, default=3.0)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--prompt", default=None, help="Override prompt.")
    parser.add_argument("--negative-prompt", default=DEFAULT_NEGATIVE_PROMPT, help="Override negative prompt.")
    parser.add_argument(
        "--prepare-mode",
        default="cover_center",
        choices=["cover_center", "cover_top", "cover_bottom", "contain_blur", "auto"],
        help="Input image framing mode before video generation.",
    )
    args = parser.parse_args()

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_video_path = args.output_dir / "ltx_first_try.mp4"
    output_frame_path = args.output_dir / "ltx_first_try_first_frame.png"
    output_mid_frame_path = args.output_dir / "ltx_first_try_mid_frame.png"
    artifact_path = args.output_dir / "summary.json"

    prompt = args.prompt or build_prompt_from_filename(args.image)
    structure_features = extract_structure_features(args.image)
    auto_shot_type = classify_shot_type(args.image)
    resolved_prepare_mode = choose_prepare_mode(args.image) if args.prepare_mode == "auto" else args.prepare_mode
    image = prepare_image(args.image, args.width, args.height, resolved_prepare_mode)
    image.save(args.output_dir / "prepared_input.png")

    artifact: dict[str, object] = {
        "image": str(args.image),
        "prepared_input": str(args.output_dir / "prepared_input.png"),
        "base_repo": args.base_repo,
        "gguf_repo": args.gguf_repo,
        "gguf_file": args.gguf_file,
        "prompt": prompt,
        "negative_prompt": args.negative_prompt,
        "prepare_mode": args.prepare_mode,
        "resolved_prepare_mode": resolved_prepare_mode,
        "auto_shot_type": auto_shot_type if args.prepare_mode == "auto" else None,
        "structure_features": structure_features,
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
        gguf_path = hf_hub_download(repo_id=args.gguf_repo, filename=args.gguf_file)
        artifact["gguf_local_path"] = gguf_path
        transformer = LTXVideoTransformer3DModel.from_single_file(
            gguf_path,
            quantization_config=GGUFQuantizationConfig(compute_dtype=torch.bfloat16),
            torch_dtype=torch.bfloat16,
        )
        pipe = LTXImageToVideoPipeline.from_pretrained(
            args.base_repo,
            transformer=transformer,
            torch_dtype=torch.bfloat16,
        )
        pipe.enable_model_cpu_offload()
        if hasattr(pipe.vae, "enable_slicing"):
            pipe.vae.enable_slicing()
        if hasattr(pipe.vae, "enable_tiling"):
            pipe.vae.enable_tiling()

        generator = torch.Generator(device="cpu").manual_seed(args.seed)
        result = pipe(
            image=image,
            prompt=prompt,
            negative_prompt=args.negative_prompt,
            width=args.width,
            height=args.height,
            num_frames=args.num_frames,
            num_inference_steps=args.steps,
            guidance_scale=args.guidance_scale,
            frame_rate=args.fps,
            max_sequence_length=128,
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

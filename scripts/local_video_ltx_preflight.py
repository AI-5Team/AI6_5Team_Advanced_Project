# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "torch",
#   "diffusers>=0.37.1",
#   "transformers>=4.51.0",
#   "accelerate>=1.8.0",
#   "sentencepiece>=0.2.0",
#   "imageio-ffmpeg>=0.6.0",
#   "huggingface_hub>=0.34.0",
#   "safetensors>=0.5.0",
# ]
# ///

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
import torch
from diffusers import AutoModel, GGUFQuantizationConfig, LTXPipeline
from huggingface_hub import HfApi


def gather_gpu_info() -> dict[str, object]:
    gpu_info = {
        "torch_cuda_available": torch.cuda.is_available(),
        "nvidia_smi_available": False,
        "device_name": None,
        "bf16_supported": torch.cuda.is_bf16_supported() if torch.cuda.is_available() else None,
        "total_vram_gb": None,
        "free_vram_gb": None,
        "notes": [],
    }
    try:
        completed = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.free",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        first_line = completed.stdout.strip().splitlines()[0]
        parts = [item.strip() for item in first_line.split(",")]
        if len(parts) >= 3:
            gpu_info["nvidia_smi_available"] = True
            gpu_info["device_name"] = parts[0]
            gpu_info["total_vram_gb"] = round(float(parts[1]) / 1024, 2)
            gpu_info["free_vram_gb"] = round(float(parts[2]) / 1024, 2)
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError, ValueError):
        gpu_info["notes"].append("nvidia-smi query failed")

    if gpu_info["torch_cuda_available"]:
        device_index = 0
        properties = torch.cuda.get_device_properties(device_index)
        free_mem, total_mem = torch.cuda.mem_get_info(device_index)
        gpu_info["device_name"] = properties.name
        gpu_info["total_vram_gb"] = round(total_mem / 1024**3, 2)
        gpu_info["free_vram_gb"] = round(free_mem / 1024**3, 2)
    elif gpu_info["nvidia_smi_available"]:
        gpu_info["notes"].append("uv script environment uses CPU-only torch; hardware GPU is still present")
    return gpu_info


def gather_model_repo_info() -> dict[str, object]:
    api = HfApi(token=os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_HUB_TOKEN"))
    gguf_repo = api.model_info("city96/LTX-Video-gguf")
    base_repo = api.model_info("Lightricks/LTX-Video")
    gguf_files = sorted(
        sibling.rfilename for sibling in gguf_repo.siblings if sibling.rfilename.lower().endswith(".gguf")
    )
    base_files = sorted(
        sibling.rfilename
        for sibling in base_repo.siblings
        if sibling.rfilename.startswith("scheduler/")
        or sibling.rfilename.startswith("tokenizer/")
        or sibling.rfilename.startswith("transformer/")
        or sibling.rfilename.startswith("vae/")
    )
    return {
        "gguf_repo": gguf_repo.id,
        "gguf_files": gguf_files,
        "base_repo": base_repo.id,
        "base_component_file_count": len(base_files),
        "sample_base_files": base_files[:20],
    }


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="Preflight check for local LTX-Video 2B / GGUF experiments.")
    parser.add_argument(
        "--artifact",
        type=Path,
        default=repo_root / "docs" / "experiments" / "artifacts" / "exp-34-local-ltx-video-preflight.json",
        help="Where to write the preflight artifact JSON.",
    )
    args = parser.parse_args()

    artifact = {
        "python": sys.version,
        "torch_version": torch.__version__,
        "diffusers_pipeline": getattr(LTXPipeline, "__name__", "LTXPipeline"),
        "gguf_quantization_class": getattr(GGUFQuantizationConfig, "__name__", "GGUFQuantizationConfig"),
        "auto_model_class": getattr(AutoModel, "__name__", "AutoModel"),
        "ffmpeg_binary": imageio_ffmpeg.get_ffmpeg_exe(),
        "gpu": gather_gpu_info(),
        "hf_model_info": gather_model_repo_info(),
        "recommendation": {
            "next_model": "city96/LTX-Video-gguf / ltx-video-2b-v0.9-Q3_K_S.gguf",
            "base_repo": "Lightricks/LTX-Video",
            "reason": "RTX 4080 Super 16GB에서 가장 가벼운 LTX 계열 first try 후보로 적합합니다.",
        },
    }

    args.artifact.parent.mkdir(parents=True, exist_ok=True)
    args.artifact.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(artifact, ensure_ascii=False, indent=2))
    print(f"artifact_path={args.artifact}")


if __name__ == "__main__":
    main()

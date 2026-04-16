from __future__ import annotations

import os
import sys
from pathlib import Path


def _patch_finetrainers_dataset() -> None:
    import finetrainers.data.dataset as dataset_module

    original_preprocess_video = dataset_module._preprocess_video

    def _patched_preprocess_video(video):
        if hasattr(video, "get_frames_in_range") and hasattr(video, "metadata"):
            metadata = video.metadata
            num_frames = getattr(metadata, "num_frames", None) or getattr(metadata, "num_frames_from_content", None)
            if num_frames is None:
                raise ValueError("torchcodec VideoDecoder metadata does not expose frame count")
            frame_batch = video.get_frames_in_range(0, min(int(num_frames), dataset_module.MAX_FRAMES), 1)
            frames = frame_batch.data
            frames = frames.float() / 127.5 - 1.0
            return frames
        return original_preprocess_video(video)

    dataset_module._preprocess_video = _patched_preprocess_video

    try:
        from torchcodec.decoders._video_decoder import VideoDecoder

        dataset_module.torchvision.io.video_reader.VideoReader = VideoDecoder
    except Exception:
        pass


def main() -> None:
    finetrainers_root = os.environ.get("FINETRAINERS_ROOT")
    if not finetrainers_root:
        raise RuntimeError("FINETRAINERS_ROOT env var is required")

    finetrainers_root_path = Path(finetrainers_root)
    if not finetrainers_root_path.exists():
        raise FileNotFoundError(f"finetrainers root not found: {finetrainers_root_path}")

    if str(finetrainers_root_path) not in sys.path:
        sys.path.insert(0, str(finetrainers_root_path))

    _patch_finetrainers_dataset()

    import train as finetrainers_train

    finetrainers_train.main()


if __name__ == "__main__":
    main()

# EXP-34 Local LTX-Video Preflight

## 1. 기본 정보

- 실험 ID: `EXP-34`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 생성형 비디오 실행 preflight`

## 2. 왜 이 작업을 했는가

- `EXP-32`에서 현재 장비의 첫 비디오 후보를 `LTX-Video 2B distilled / GGUF`로 정리했습니다.
- 다음 단계는 바로 큰 weights를 받는 게 아니라, 이 저장소에서 실제로 실행 가능한 preflight 스크립트를 먼저 갖추는 것이었습니다.
- 따라서 `LTX-Video 2B / GGUF`용 최소 preflight 스크립트를 추가하고 실제로 실행했습니다.

## 3. baseline

### 고정한 조건

1. 하드웨어: `RTX 4080 Super 16GB / RAM 64GB`
2. 모델 후보: `city96/LTX-Video-gguf`
3. base repo: `Lightricks/LTX-Video`
4. 목적: 실제 생성 전 `의존성 / GPU 인식 / HF repo 구성` 확인

## 4. 무엇을 바꿨는가

- `scripts/local_video_ltx_preflight.py`
  - `uv run`으로 바로 실행 가능한 PEP 723 스크립트 추가
  - `diffusers`, `transformers`, `sentencepiece`, `imageio-ffmpeg`, `huggingface_hub` preflight
  - `LTXPipeline`, `GGUFQuantizationConfig` import 체크
  - `city96/LTX-Video-gguf`의 GGUF 파일 목록과 `Lightricks/LTX-Video` base component 파일 목록을 artifact로 저장
  - GPU 정보는 `nvidia-smi` 기준으로 다시 보정

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-34-local-ltx-video-preflight.json`

### 확인된 것

1. preflight 스크립트는 정상 실행됐습니다.
2. `city96/LTX-Video-gguf`에는 `Q3_K_S`, `Q4_K_M`, `Q8_0` 등 여러 GGUF 파일이 존재합니다.
3. `Lightricks/LTX-Video` base repo의 tokenizer/scheduler/transformer/vae 구성도 확인됐습니다.
4. 현재 first try 추천 파일은 `ltx-video-2b-v0.9-Q3_K_S.gguf`로 정리했습니다.

### 중요한 제약

1. `uv` 임시 환경이 잡은 `torch`는 `2.11.0+cpu`였습니다.
2. 즉 preflight는 통과했지만, **이 상태로는 실제 GPU 생성까지 바로 이어지지 않습니다.**
3. 다만 `nvidia-smi` 기준으로 물리 GPU 자체는 정상이며, 현재 사용 가능 VRAM도 확인됐습니다.

## 6. 실패/제약

1. 이번 실험은 실제 비디오 생성이 아니라 preflight입니다.
2. `uv` 임시 환경은 CPU-only torch를 잡았기 때문에, 다음 단계에서는 별도 GPU torch 환경이 필요합니다.
3. 즉 현재 blocker는 모델 weights가 아니라 **GPU-enabled Python runtime 분리**입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `LTX-Video 2B / GGUF`로 가는 실행 경로 자체는 유효합니다.
  - 다만 다음 단계는 model download 전에 `GPU torch`가 있는 전용 환경을 만드는 것입니다.
  - 현재 repo 기준으로는 `preflight -> GPU env 분리 -> 실제 1회 생성` 순서가 맞습니다.

## 8. 다음 액션

1. 다음은 `GPU-enabled local video env`를 별도로 만듭니다.
2. 그 다음 `ltx-video-2b-v0.9-Q3_K_S.gguf` + `Lightricks/LTX-Video` 조합으로 실제 1회 생성에 들어갑니다.
3. 이 경로가 되면 그 다음 후보로 `CogVideoX-5B-I2V`를 붙입니다.

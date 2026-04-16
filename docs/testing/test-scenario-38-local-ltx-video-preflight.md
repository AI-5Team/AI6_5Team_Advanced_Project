# 테스트 시나리오 38 - Local LTX-Video Preflight

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-38`

## 2. 테스트 목적

- `LTX-Video 2B / GGUF`를 이 저장소에서 로컬 실험할 수 있는 최소 preflight 경로가 실제로 동작하는지 확인합니다.

## 3. 수행 항목

1. `uv run scripts/local_video_ltx_preflight.py`

## 4. 결과

- preflight 스크립트: 실행 완료
- 생성 artifact:
  - `exp-34-local-ltx-video-preflight.json`

## 5. 관찰 내용

1. `LTXPipeline`, `GGUFQuantizationConfig` import는 통과했습니다.
2. `city96/LTX-Video-gguf` GGUF 파일 목록을 확인했습니다.
3. 물리 GPU는 보였지만, `uv` 환경의 torch는 CPU-only였습니다.

## 6. 실패/제약

1. 아직 실제 비디오 생성은 아닙니다.
2. 다음 단계 전에 GPU-enabled Python runtime을 별도로 준비해야 합니다.

## 7. 개선 포인트

1. 다음은 GPU torch 기반 전용 로컬 비디오 환경을 만드는 작업입니다.
2. 그 후 `LTX-Video 2B / GGUF` 실제 1회 생성으로 넘어갑니다.

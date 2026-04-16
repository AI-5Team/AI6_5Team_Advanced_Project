# 테스트 시나리오 40 - Local LTX-Video 2B GGUF First Try

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-40`

## 2. 테스트 목적

- 현재 로컬 GPU 환경에서 `LTX-Video 2B / GGUF` 이미지-투-비디오가 실제로 1회 완주하는지 확인합니다.

## 3. 수행 항목

1. `python -m pip install --user diffusers==0.37.1 sentencepiece imageio-ffmpeg`
2. `python -m pip install --user "gguf>=0.10.0"`
3. `python scripts/local_video_ltx_first_try.py --num-frames 17 --steps 6 --fps 8`

## 4. 결과

- 실행 상태: 성공
- 생성 artifact:
  - `exp-36-local-ltx-video-first-try/ltx_first_try.mp4`
  - `exp-36-local-ltx-video-first-try/ltx_first_try_first_frame.png`
  - `exp-36-local-ltx-video-first-try/ltx_first_try_mid_frame.png`
  - `exp-36-local-ltx-video-first-try/summary.json`

## 5. 관찰 내용

1. `RTX 4080 SUPER 16GB`에서 실제 17프레임 샘플이 생성됐습니다.
2. 첫 프레임은 입력 음식 사진의 구조를 비교적 잘 유지했습니다.
3. 중간 프레임에는 약한 고스팅이 보였습니다.

## 6. 실패/제약

1. 최초 시도에서는 GGUF 파일 로딩 방식과 `gguf` 패키지 때문에 실패했습니다.
2. Windows Hugging Face symlink warning이 나왔습니다.
3. 이번 실행은 짧은 smoke test라서 품질 확정 실험은 아닙니다.

## 7. 개선 포인트

1. 다음은 `steps` 또는 `prompt length` 한 레버만 바꿔 `LTX` 품질을 올릴 수 있는지 봅니다.
2. 그 다음 `CogVideoX-5B-I2V`와 비교해 현재 장비의 실전 후보를 정합니다.

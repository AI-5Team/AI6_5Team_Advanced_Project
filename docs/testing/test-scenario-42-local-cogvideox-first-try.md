# 테스트 시나리오 42 - Local CogVideoX First Try

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-42`

## 2. 테스트 목적

- `CogVideoX-5B-I2V`가 현재 로컬 GPU 환경에서 실제로 한 번 완주하는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_cogvideox_first_try.py --num-frames 16 --steps 8 --fps 8`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-38-local-cogvideox-first-try/summary.json`
  - `exp-38-local-cogvideox-first-try/cogvideox_first_try.mp4`
  - `exp-38-local-cogvideox-first-try/cogvideox_first_try_first_frame.png`
  - `exp-38-local-cogvideox-first-try/cogvideox_first_try_mid_frame.png`

## 5. 관찰 내용

1. 실행 자체는 가능했습니다.
2. 다만 첫 프레임부터 격자형 artifact가 강했고, `LTX`보다 음식 구조 보존이 약했습니다.
3. 실행 시간도 `LTX`보다 훨씬 길었습니다.

## 6. 실패/제약

1. 품질이 현재 baseline 후보 수준은 아닙니다.
2. 첫 실행에 download 시간이 크게 포함됐습니다.

## 7. 개선 포인트

1. 현재 주력 baseline은 계속 `LTX`가 맞습니다.
2. `CogVideoX`는 설정 재조정 후 재시도 후보로 둡니다.

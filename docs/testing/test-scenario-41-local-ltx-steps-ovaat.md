# 테스트 시나리오 41 - Local LTX Steps OVAT

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-41`

## 2. 테스트 목적

- `LTX-Video 2B / GGUF`에서 `steps`만 바꿨을 때 실제 품질 차이가 생기는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_first_try.py --num-frames 17 --steps 6 --fps 8 --output-dir docs/experiments/artifacts/exp-37-local-ltx-video-steps-ovaat/steps-6`
2. `python scripts/local_video_ltx_first_try.py --num-frames 17 --steps 10 --fps 8 --output-dir docs/experiments/artifacts/exp-37-local-ltx-video-steps-ovaat/steps-10`

## 4. 결과

- 두 실행 모두 성공
- artifact:
  - `steps-6/summary.json`
  - `steps-10/summary.json`

## 5. 관찰 내용

1. 실행 시간 차이는 크지 않았습니다.
2. `steps=10`이 더 선명해지기보다 오히려 일부 고스팅이 더 커 보였습니다.

## 6. 실패/제약

1. 단일 입력 이미지 기준 smoke test입니다.
2. 정량 지표는 heuristic 보조값입니다.

## 7. 개선 포인트

1. 다음 `LTX` 레버는 `steps`보다 `prompt length` 또는 `num_frames`가 더 적절합니다.

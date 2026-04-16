# 테스트 시나리오 49 - Local LTX micro movement OVAT

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-49`

## 2. 테스트 목적

- `static close-up` baseline 위에 `subtle camera drift`를 추가했을 때 실제로 개선이 되는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_camera_motion_ovaat.py --offline --baseline-motion "static close-up, minimal camera movement" --variant-motion "static close-up, subtle camera drift" --output-dir docs/experiments/artifacts/exp-46-local-ltx-video-micro-movement-ovaat`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-46-local-ltx-video-micro-movement-ovaat/summary.json`
  - `baseline-push-in/ltx_first_try_mid_frame.png`
  - `variant-static-close-up/ltx_first_try_mid_frame.png`

## 5. 관찰 내용

1. `subtle camera drift`는 오히려 음식 구조 보존을 악화시켰습니다.
2. 실행 시간 차이는 거의 없었습니다.
3. 따라서 현재 baseline은 그대로 `minimal camera movement`를 유지하는 편이 맞습니다.

## 6. 실패/제약

1. 단일 이미지 1장 기준입니다.
2. clip 전체 체감보다 frame 품질 우선으로 판단했습니다.

## 7. 개선 포인트

1. 다음 레버는 motion보다 `steam intensity` 또는 `lighting phrase`가 적절합니다.

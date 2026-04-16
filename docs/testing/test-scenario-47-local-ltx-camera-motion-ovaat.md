# 테스트 시나리오 47 - Local LTX camera motion OVAT

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-47`

## 2. 테스트 목적

- `LTX-Video 2B / GGUF`에서 `camera motion phrase`만 바꿨을 때 frame 품질 차이를 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_camera_motion_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-44-local-ltx-video-camera-motion-ovaat/summary.json`
  - `baseline-push-in/ltx_first_try_mid_frame.png`
  - `variant-static-close-up/ltx_first_try_mid_frame.png`

## 5. 관찰 내용

1. `static close-up, minimal camera movement` 쪽이 `slow push-in`보다 음식 구조 보존이 더 좋았습니다.
2. 실행 시간 차이는 거의 없었습니다.
3. 따라서 현재 로컬 LTX food shot에서는 더 정적인 motion phrase가 유리합니다.

## 6. 실패/제약

1. 단일 이미지 1장 기준입니다.
2. clip 전체가 지나치게 정적으로 느껴지는지는 별도 확인이 필요합니다.

## 7. 개선 포인트

1. 다음 레버는 `micro camera movement` 또는 `steam intensity`가 적절합니다.
2. 다음 판단은 frame뿐 아니라 clip 전체 움직임 기준으로도 봐야 합니다.

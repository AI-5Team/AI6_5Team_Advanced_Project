# 테스트 시나리오 45 - Local LTX num_frames OVAT

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-45`

## 2. 테스트 목적

- `LTX-Video 2B / GGUF`에서 `num_frames`만 바꿨을 때 실행 시간과 frame 품질 차이를 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_num_frames_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-42-local-ltx-video-num-frames-ovaat/summary.json`
  - `frames-17/summary.json`
  - `frames-25/summary.json`

## 5. 관찰 내용

1. `25프레임`도 현재 장비에서 문제없이 실행됐습니다.
2. 실행 시간 차이는 `0.2초` 수준이었습니다.
3. mid frame 기준으로는 `25프레임`이 `17프레임`보다 음식 구조 보존이 조금 더 좋았습니다.

## 6. 실패/제약

1. 단일 이미지 1장만 사용했습니다.
2. clip 전체 자연스러움은 이번 테스트에 포함하지 않았습니다.

## 7. 개선 포인트

1. 다음은 `camera motion phrase`를 한 레버로 바꿔 보는 편이 적절합니다.
2. `25프레임` 유지 여부는 clip 전체 시청 기준으로 한 번 더 판단해야 합니다.

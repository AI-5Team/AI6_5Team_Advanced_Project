# 테스트 시나리오 59 - local LTX negative prompt OVAT

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-59`

## 2. 테스트 목적

- `LTX-Video 2B / GGUF`에서 stronger negative prompt가 실제로 artifact 억제에 도움이 되는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_negative_prompt_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-56-local-ltx-video-negative-prompt-ovaat/summary.json`
  - `baseline-default-negative/ltx_first_try_mid_frame.png`
  - `variant-stronger-negative/ltx_first_try_mid_frame.png`

## 5. 관찰 내용

1. stronger negative prompt는 속도는 약간 줄였지만 품질은 크게 악화됐습니다.
2. mid frame MSE가 `246.90 -> 384.47`로 나빠졌고 edge variance도 떨어졌습니다.
3. 따라서 현재 baseline에 stronger negative prompt를 넣는 것은 보류가 맞습니다.

## 6. 실패/제약

1. 단일 이미지 1장 기준입니다.
2. stronger negative 묶음 안에서 어떤 phrase가 가장 해로운지는 아직 분리하지 않았습니다.

## 7. 개선 포인트

1. 다음에는 메뉴 사진을 바꿔 같은 baseline 재현성을 확인합니다.
2. negative prompt 자체보다 입력 이미지/seed 쪽 변수를 보는 편이 더 맞습니다.

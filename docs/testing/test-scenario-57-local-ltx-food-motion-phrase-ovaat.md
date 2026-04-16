# 테스트 시나리오 57 - local LTX food motion phrase OVAT

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-57`

## 2. 테스트 목적

- `LTX-Video 2B / GGUF`에서 `food motion phrase`를 더 구체화하면 food-shot 품질이 좋아지는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_food_motion_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-54-local-ltx-video-food-motion-phrase-ovaat/summary.json`
  - `baseline-realistic-motion/ltx_first_try_mid_frame.png`
  - `variant-sizzling-motion/ltx_first_try_mid_frame.png`

## 5. 관찰 내용

1. `subtle sizzling food motion`은 실행 시간은 약간 짧았지만 품질 이득은 만들지 못했습니다.
2. mid frame MSE와 edge variance 모두 baseline이 더 좋았습니다.
3. 따라서 motion phrase는 지금 단계에서 상위 레버가 아닙니다.

## 6. 실패/제약

1. 단일 이미지 1장 기준입니다.
2. 다른 음식군에서 재현성은 아직 미확인입니다.

## 7. 개선 포인트

1. 다음에는 `negative phrase`를 한 레버로 봅니다.
2. 메뉴 사진을 바꿔 같은 실험을 다시 확인합니다.

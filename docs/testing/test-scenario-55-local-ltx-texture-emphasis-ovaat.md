# 테스트 시나리오 55 - local LTX texture emphasis OVAT

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-55`

## 2. 테스트 목적

- `LTX-Video 2B / GGUF`에서 explicit texture phrase가 실제로 food-shot 품질을 올리는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_texture_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-52-local-ltx-video-texture-emphasis-ovaat/summary.json`
  - `baseline-no-texture/ltx_first_try_mid_frame.png`
  - `variant-crispy-texture/ltx_first_try_mid_frame.png`

## 5. 관찰 내용

1. `detailed crispy breading texture`는 이번 샘플에서 quality gain을 만들지 못했습니다.
2. mid frame MSE와 edge variance 모두 baseline이 더 좋았습니다.
3. 따라서 현재 baseline에 texture phrase를 추가하는 것은 보류가 맞습니다.

## 6. 실패/제약

1. 단일 이미지 1장 기준입니다.
2. 다른 메뉴군에서는 결과가 달라질 수 있습니다.

## 7. 개선 포인트

1. 다음에는 `food motion phrase` 또는 `negative phrase`를 한 레버로 봅니다.
2. texture 레버는 음식 종류를 바꿔 다시 보는 편이 더 적절합니다.

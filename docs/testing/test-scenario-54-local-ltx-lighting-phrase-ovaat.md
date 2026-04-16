# 테스트 시나리오 54 - local LTX lighting phrase OVAT

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-54`

## 2. 테스트 목적

- `LTX-Video 2B / GGUF`에서 `lighting phrase`만 바꿨을 때 음식 구조 보존이 달라지는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_lighting_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-51-local-ltx-video-lighting-phrase-ovaat/summary.json`
  - `baseline-warm-lighting/ltx_first_try_mid_frame.png`
  - `variant-bright-lighting/ltx_first_try_mid_frame.png`

## 5. 관찰 내용

1. `bright tabletop lighting`가 `warm restaurant lighting`보다 mid frame MSE가 낮았습니다.
2. edge variance도 더 높아서 음식과 그릇 경계가 조금 더 또렷하게 유지됐습니다.
3. 실행 시간도 소폭 더 짧았습니다.

## 6. 실패/제약

1. 단일 이미지 1장 기준입니다.
2. clip 전체를 보고 느끼는 분위기 차이까지는 아직 충분히 보지 않았습니다.

## 7. 개선 포인트

1. 다음에는 `texture emphasis` 또는 `food motion phrase`를 한 레버로 봅니다.
2. 다른 음식 사진 1~2장으로 재현성을 확인합니다.

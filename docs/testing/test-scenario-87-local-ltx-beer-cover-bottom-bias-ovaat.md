# 테스트 시나리오 87 - local LTX beer cover bottom bias OVAT

## 1. 테스트 정보

- 일자: `2026-04-09`
- 진행자: Codex
- 시나리오 ID: `TS-87`

## 2. 테스트 목적

- `맥주` baseline에서 `cover_center`보다 `cover_bottom`이 더 적합한지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_beer_cover_bottom_bias_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-84-local-ltx-beer-cover-bottom-bias-ovaat/summary.json`

## 5. 관찰 내용

1. `cover_bottom`이 `cover_center`보다 `mid-frame MSE`, `edge variance` 모두 더 좋았습니다.
2. prepared input 단계에서도 label과 glass 하단 정보가 더 크게 살아났습니다.

## 6. 실패/제약

1. `맥주` 1장 기준입니다.

## 7. 개선 포인트

1. `bottom-heavy bottle+glass` 케이스는 `cover_center`보다 `cover_bottom`으로 보는 편이 맞습니다.

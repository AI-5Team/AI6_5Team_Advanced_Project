# 테스트 시나리오 51 - Local LTX steam intensity OVAT

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-51`

## 2. 테스트 목적

- `gentle steam`과 `strong steam cloud` 중 어떤 표현이 음식 구조 보존에 더 유리한지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_steam_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-48-local-ltx-video-steam-intensity-ovaat/summary.json`
  - `baseline-gentle-steam/ltx_first_try_mid_frame.png`
  - `variant-strong-steam/ltx_first_try_mid_frame.png`

## 5. 관찰 내용

1. 이번 샘플에서는 `strong steam cloud` 쪽이 오히려 더 안정적이었습니다.
2. 실행 시간 차이는 거의 없었습니다.
3. 따라서 `steam intensity`는 유지 가능한 유효 레버 후보입니다.

## 6. 실패/제약

1. 단일 이미지 1장 기준입니다.
2. 다른 음식에서 같은 경향이 유지되는지는 추가 검증이 필요합니다.

## 7. 개선 포인트

1. 다음은 `lighting phrase`를 한 변수로 보는 편이 적절합니다.
2. `steam`은 다른 음식 샘플로 재현성을 확인해야 합니다.

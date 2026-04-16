# 테스트 시나리오 81 - local LTX beer drink motion phrase OVAT

## 1. 테스트 정보

- 일자: `2026-04-09`
- 진행자: Codex
- 시나리오 ID: `TS-81`

## 2. 테스트 목적

- `맥주` 샘플에서 `realistic drink commercial motion`이 품질 저하 원인인지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_beer_drink_motion_phrase_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-78-local-ltx-beer-drink-motion-phrase-ovaat/summary.json`

## 5. 관찰 내용

1. `still life beverage shot` variant가 크게 더 좋았습니다.
2. metric뿐 아니라 mid frame 시각 결과에서도 foam/glass 흔들림이 줄었습니다.

## 6. 실패/제약

1. `맥주` 1장 기준입니다.

## 7. 개선 포인트

1. 현재 reusable runner에서는 `맥주`만 `still life beverage shot` 예외로 두는 편이 맞습니다.

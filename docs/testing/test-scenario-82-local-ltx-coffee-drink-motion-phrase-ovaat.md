# 테스트 시나리오 82 - local LTX coffee drink motion phrase OVAT

## 1. 테스트 정보

- 일자: `2026-04-09`
- 진행자: Codex
- 시나리오 ID: `TS-82`

## 2. 테스트 목적

- `맥주`에서 좋았던 `still life beverage shot`가 `커피`에도 유지되는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_coffee_drink_motion_phrase_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-79-local-ltx-coffee-drink-motion-phrase-ovaat/summary.json`

## 5. 관찰 내용

1. `커피`도 `still life beverage shot` variant가 더 좋았습니다.
2. 따라서 이 레버는 `맥주 전용`이 아니라 drink lane 공통 baseline 후보입니다.

## 6. 실패/제약

1. drink lane 근거는 아직 2장입니다.

## 7. 개선 포인트

1. reusable runner의 glass drink baseline을 `still life beverage shot`으로 두는 편이 맞습니다.

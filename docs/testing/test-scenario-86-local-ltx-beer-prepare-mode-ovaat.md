# 테스트 시나리오 86 - local LTX beer prepare mode OVAT

## 1. 테스트 정보

- 일자: `2026-04-09`
- 진행자: Codex
- 시나리오 ID: `TS-86`

## 2. 테스트 목적

- `맥주` baseline에서 `prepare_mode`가 실제 병목인지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_beer_prepare_mode_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-83-local-ltx-beer-prepare-mode-ovaat/summary.json`

## 5. 관찰 내용

1. `cover_center`가 `cover_top`보다 `mid-frame MSE`, `edge variance` 모두 더 좋았습니다.
2. prepared input 단계에서도 bottle label과 glass 영역이 더 크게 살아났습니다.

## 6. 실패/제약

1. `맥주` 1장 기준입니다.

## 7. 개선 포인트

1. `bottom-heavy bottle+glass` 케이스는 `cover_top`이 아니라 `cover_center`로 분기하는 편이 맞습니다.

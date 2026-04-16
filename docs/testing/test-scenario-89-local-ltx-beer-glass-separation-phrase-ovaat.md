# 테스트 시나리오 89 - local LTX beer glass separation phrase OVAT

## 1. 테스트 정보

- 일자: `2026-04-09`
- 진행자: Codex
- 시나리오 ID: `TS-89`

## 2. 테스트 목적

- `맥주` baseline에서 bottle/glass separation phrase가 추가 개선을 만드는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_beer_glass_separation_phrase_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-86-local-ltx-beer-glass-separation-phrase-ovaat/summary.json`

## 5. 관찰 내용

1. separation phrase는 baseline 대비 사실상 개선이 없었습니다.
2. 따라서 현재 baseline 위에서는 유효 레버가 아닙니다.

## 6. 실패/제약

1. `맥주` 1장 기준입니다.

## 7. 개선 포인트

1. 다음은 separation prompt가 아니라 다른 샘플군이나 다른 입력 레버를 보는 편이 맞습니다.

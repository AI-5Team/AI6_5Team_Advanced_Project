# 테스트 시나리오 73 - local LTX drink top bias generalization

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-73`

## 2. 테스트 목적

- `cover_top`이 커피 전용 예외인지, drink subset에서 일반화 가능한지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_drink_top_bias_generalization.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-70-local-ltx-drink-top-bias-generalization/summary.json`

## 5. 관찰 내용

1. `커피`, `맥주` 둘 다 `cover_top`이 더 좋았습니다.
2. 따라서 `glass drink candidate -> cover_top`은 현재 데이터 기준으로 일반 규칙 후보가 됩니다.

## 6. 실패/제약

1. drink 샘플은 아직 2장뿐입니다.

## 7. 개선 포인트

1. auto classifier가 `맥주`도 `cover_top`으로 잡도록 보정해야 합니다.

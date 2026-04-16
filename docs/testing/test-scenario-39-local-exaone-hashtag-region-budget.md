# 테스트 시나리오 39 - Local EXAONE Hashtag Region Budget

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-39`

## 2. 테스트 목적

- `EXAONE 3.5 7.8B`에서 `hashtag/caption region budget` 한 레버가 `T02 promotion`의 지역 반복을 줄이는지 확인합니다.

## 3. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py -q`
2. `uv run --project services/worker python scripts/run_prompt_experiment.py --experiment-id EXP-35 --api-key-env OLLAMA_HOST`

## 4. 결과

- 테스트: 통과
- 실험 artifact:
  - `exp-35-local-exaone-3-5-7-8b-prompt-lever-experiment-promotion-hashtag-region-budget.json`

## 5. 관찰 내용

1. baseline은 score `100.0`이었지만 scene-plan 기준 `over-limit`는 남아 있었습니다.
2. variant는 hashtags 개수는 5개로 맞췄지만 지역명 반복은 줄지 않았습니다.
3. 한글 깨짐은 이번 샘플에서 보이지 않았습니다.

## 6. 실패/제약

1. 이번 레버는 실제 개선에 실패했습니다.
2. EXAONE는 지역명 제약 phrasing을 안정적으로 따르지 않았습니다.

## 7. 개선 포인트

1. EXAONE는 prompt phrasing보다 후처리 정규화/guardrail 쪽이 더 유효해 보입니다.
2. 다음 비교는 다른 모델과의 baseline 차이를 보는 편이 효율적입니다.

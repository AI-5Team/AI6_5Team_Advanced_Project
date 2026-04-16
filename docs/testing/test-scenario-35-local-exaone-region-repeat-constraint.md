# 테스트 시나리오 35 - Local EXAONE Region Repeat Constraint

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-35`

## 2. 테스트 목적

- 로컬 `EXAONE 3.5 7.8B`에서 `region_repeat_constraint` 한 레버가 실제로 `T02 promotion` 지역 반복을 줄이는지 확인합니다.

## 3. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py`
2. `uv run --project services/worker python scripts/run_prompt_experiment.py --experiment-id EXP-31 --api-key-env OLLAMA_HOST`

## 4. 결과

- pytest: 통과
- `EXP-31`: 실행 완료
- 생성 artifact:
  - `exp-31-local-exaone-3-5-7-8b-prompt-lever-experiment-promotion-region-repeat-constraint.json`

## 5. 관찰 내용

1. baseline과 variant 모두 한글 깨짐은 보이지 않았습니다.
2. 하지만 `region_repeat_constraint`를 넣어도 지역 반복은 줄지 않았습니다.
3. over-limit scene 수는 일부 줄었지만 핵심 목표는 달성하지 못했습니다.

## 6. 실패/제약

1. 이번 실험은 가설 실패입니다.
2. `EXAONE 3.5 7.8B`는 이 phrasing의 지역 제약에 잘 반응하지 않았습니다.

## 7. 개선 포인트

1. 다음 레버는 `output constraint`나 `hashtag rule`처럼 더 직접적인 구조 제약이 맞습니다.
2. `region_repeat_constraint`는 같은 phrasing으로 반복하지 않습니다.

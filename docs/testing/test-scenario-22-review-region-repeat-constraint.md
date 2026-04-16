# 테스트 시나리오 22 - Review Region Repeat Constraint

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-22`

## 2. 테스트 목적

- `EXP-18`이 `T04 review`에서 지역 반복 제약만 추가하는지 확인합니다.
- 지역 반복 제약이 실제 `region repeat` 초과를 줄이는지 검증합니다.

## 3. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py`
2. `uv run --project services/worker python scripts/run_prompt_experiment.py --experiment-id EXP-18`
3. artifact JSON 확인

## 4. 결과

- prompt harness tests: 통과
- `EXP-18` 실행: 통과
- artifact:
  - `docs/experiments/artifacts/exp-18-gemma-4-prompt-lever-experiment-review-region-repeat-constraint.json`

## 5. 관찰 내용

1. region repeat constraint variant는 `region repeat 3 -> 2`로 줄였습니다.
2. 같은 조건에서 `failed_checks`를 제거했습니다.
3. `review` 템플릿에서는 이 레버가 현재 가장 유의미해 보입니다.

## 6. 실패/제약

1. 단일 실행 1회입니다.
2. CTA heuristic은 colloquial 표현을 보수적으로 봅니다.

## 7. 개선 포인트

1. 다음은 `CTA 강도`를 한 레버로 분리합니다.
2. 이후 `promotion`과 `review`의 우선 레버 차이를 비교 표로 정리합니다.

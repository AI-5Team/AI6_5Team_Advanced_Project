# 테스트 시나리오 30 - Review Model Comparison

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-30`

## 2. 테스트 목적

- `T04 review`에서 `Gemma 4`와 `gpt-5-mini`를 같은 프롬프트 조건으로 비교합니다.
- model-only 비교가 promotion뿐 아니라 review에서도 의미 있는지 확인합니다.

## 3. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py`
2. `uv run --project services/worker python scripts/run_model_comparison_experiment.py --experiment-id EXP-26`

## 4. 결과

- pytest: 통과
- `EXP-26`: 실행 완료
- 생성 artifact:
  - `exp-26-service-aligned-review-model-comparison.json`

## 5. 관찰 내용

1. `Gemma 4`는 CTA 표현이 `면치러 가기`로 나와 action keyword heuristic을 통과하지 못했습니다.
2. `gpt-5-mini`는 failed check는 없었지만 scene budget과 반복 문제가 남았습니다.
3. `review` 축에서는 score와 scene-plan 안정성이 일치하지 않는 문제가 더 분명하게 드러났습니다.

## 6. 실패/제약

1. 단일 실행 1회입니다.
2. 평가 점수만으로는 render-readiness를 제대로 설명하지 못합니다.

## 7. 개선 포인트

1. 다음은 `gpt-5-mini` output constraint 실험으로 바로 이어갑니다.
2. 이후 `Gemini 2.5 Flash` format 안정화 실험을 다시 진행합니다.

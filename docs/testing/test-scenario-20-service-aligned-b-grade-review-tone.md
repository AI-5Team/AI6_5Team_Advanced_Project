# 테스트 시나리오 20 - Service-Aligned B-Grade Review Tone

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-20`

## 2. 테스트 목적

- `EXP-16`이 `T04 review`의 실제 슬롯 구조를 올바르게 요구하는지 확인합니다.
- `B급 review tone guidance`가 `scene-plan` 기준으로 어떤 trade-off를 만드는지 검증합니다.

## 3. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py`
2. `uv run --project services/worker python scripts/run_prompt_experiment.py --experiment-id EXP-16`
3. artifact JSON 확인

## 4. 결과

- prompt harness tests: 통과
- `EXP-16` 실행: 통과
- artifact:
  - `docs/experiments/artifacts/exp-16-gemma-4-prompt-lever-experiment-service-aligned-b-grade-review-tone.json`

## 5. 관찰 내용

1. `B급 review tone guidance`는 `review_quote`, `product_name`, `cta` 길이는 줄였습니다.
2. 하지만 지역 반복이 `2 -> 3`으로 늘어 copy score가 다시 내려갔습니다.
3. 즉, `review` 템플릿에서는 같은 톤 레버가 바로 승리하지 않았습니다.

## 6. 실패/제약

1. 단일 실행 1회입니다.
2. CTA heuristic은 `확인하기` 계열을 보수적으로 봅니다.

## 7. 개선 포인트

1. 다음은 `slot 길이 제한`을 한 레버로 분리합니다.
2. 이후 `지역 반복 제약`을 따로 봅니다.

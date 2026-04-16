# 테스트 시나리오 28 - Google Model Comparison

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-28`

## 2. 테스트 목적

- Google family 모델만 바꿨을 때 output format, 길이 예산, CTA/scene-plan 안정성이 어떻게 달라지는지 확인합니다.

## 3. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py`
2. `uv run --project services/worker python scripts/run_model_comparison_experiment.py --experiment-id EXP-24`

## 4. 결과

- pytest: 통과
- `EXP-24`: 실행 완료
- 생성 artifact:
  - `exp-24-service-aligned-promotion-google-model-comparison.json`

## 5. 관찰 내용

1. `Gemma 4`는 안정적이지만 지역 반복 문제는 남습니다.
2. `Gemini 2.5 Flash`는 JSON output format failure가 발생했습니다.
3. `Gemini 2.5 Flash-Lite`는 빠르지만 모든 scene가 길이 초과였습니다.

## 6. 실패/제약

1. 단일 실행 1회입니다.
2. `Flash` 계열은 내용 품질 이전에 output format/length 안정성부터 보완이 필요합니다.

## 7. 개선 포인트

1. `review(T04)` 축에서도 model-only 비교를 한 번 더 확인합니다.
2. `Flash` 계열은 output format constraint를 별도 레버로 분리합니다.

# Test Scenario 159

## 목적

- `EXP-158` candidate가 region anchor를 드러내면서도 strict location policy를 깨지 않는지 확인합니다.

## 실행

- `python scripts/run_google_prompt_experiment_with_transport.py --experiment-id EXP-158 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`
- `python scripts/run_google_prompt_variant_repeatability_with_transport.py --experiment-id EXP-158 --repeat 3 --timeout-sec 90 --max-retries 1 --retry-backoff-sec 3`

## 기대 결과

- baseline/candidate 모두 `score=100.0`
- `detail_location_leak_count=0`
- `over_limit_scene_count=0`
- candidate는 첫 훅에서 region anchor를 보여야 합니다.

## 실제 결과

- baseline: `3/3`, `avg_score=100.0`
- candidate: `3/3`, `avg_score=100.0`
- candidate sample hooks:
  - `성수동에서 이거 보셨나요?`
  - `성수동에서 이거 보셨나요?`
  - `성수동에서 이거 보셨나요?`

## 판정

- 통과

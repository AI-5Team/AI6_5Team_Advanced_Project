# EXP-223 Review Surface Lock Current Baseline Model Comparison

## 배경

- `EXP-131` 이후 review fallback은 `gpt-5-mini + surface-locked exact region anchor` 쪽으로 굳어졌습니다.
- 하지만 이 판단이 `모델 차이` 때문인지, 아니면 `예전 prompt 차이` 때문인지는 다시 분리해서 볼 필요가 있었습니다.
- quick-option baseline catalog를 모두 닫은 지금 시점에서는, 현재 실제로 채택한 review prompt를 고정하고 모델만 다시 바꿔보는 재평가가 맞습니다.

## 목표

- `T04 review / b_grade_fun / highlightPrice=false / shorterCopy=true / emphasizeRegion=false` 기준으로, 현재 채택한 `surface-locked exact region anchor` prompt를 고정합니다.
- 같은 prompt에서 `Gemma 4`와 `gpt-5-mini`를 직접 비교해, review fallback 분리가 여전히 모델 품질 차이인지 확인합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
  - `services/worker/tests/test_prompt_harness.py`
- 추가 model comparison:
  - `EXP-223`
- 고정 prompt:
  - `fixed_review_surface_locked_exact_region_anchor`
- 비교 모델:
  - `google / models/gemma-4-31b-it`
  - `openai / gpt-5-mini`

## 실행

- `python scripts/run_model_comparison_experiment.py --experiment-id EXP-223`
- `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py -q`
- `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py -q`
- `uv run --project services/api pytest services/api/tests/test_api_smoke.py -q`

artifact:

- `docs/experiments/artifacts/exp-223-review-surface-lock-current-baseline-model-comparison.json`

## 결과

| model | score | latency_ms | hook | cta | failed |
|---|---:|---:|---|---|---|
| deterministic reference | `93.3` | `0` | `성수동 기준 다시 찾게 되는 한 줄 후기` | `지금 바로 들러보세요` | `region repeated more than allowed` |
| Gemma 4 | `100.0` | `59218` | `한 번 먹고 바로 기억나요` | `저장하고 지금 방문해` | 없음 |
| GPT-5 Mini | `100.0` | `6125` | `한 번 먹고 기억나요` | `방문해보기` | 없음 |

세부 관찰:

- Gemma 4
  - captions:
    - `성수동 가면 무조건 여기부터 가세요.`
    - `국물 한 입 먹자마자 뇌 정지 옴.`
    - `친구한테 제보받고 갔는데 진짜임.`
  - scene headline 길이: `14 / 13 / 11`
  - 지역 반복: `2`
  - detail-location leak: `0`
- GPT-5 Mini
  - captions:
    - `국물 한모금에 멍하게 좋아짐`
    - `면이 쫄깃해서 또 찾게 되는 라멘`
    - `성수동에서 가볍게 한 그릇`
  - scene headline 길이: `11 / 11 / 5`
  - 지역 반복: `2`
  - detail-location leak: `0`

## 해석

1. 현재 채택한 review surface-lock prompt는 더 이상 `gpt-5-mini만 통과하는 prompt`가 아니었습니다.
2. 같은 prompt에서 Gemma 4도 single run 기준으로는 strict fallback 품질선을 통과했습니다.
3. 즉 예전의 provider 분리에는 `모델 자체`뿐 아니라 `prompt family 차이`도 분명히 섞여 있었습니다.
4. 다만 Gemma 4 latency가 약 `59초`로 매우 높아, 운영 판단은 single-run 품질만으로 끝낼 수 없습니다.

## 결론

- 품질 관점 single run만 보면 review current prompt는 `Gemma 4`와 `gpt-5-mini`가 모두 통과선입니다.
- 따라서 다음 판단 기준은 `누가 통과하느냐`보다 `누가 기본 transport에서 더 안정적으로 반복 통과하느냐`로 넘어갑니다.

# Test Scenario 147

## 제목

Gemma promotion strict anchor transport profile 비교

## 목적

- `EXP-144` prompt를 그대로 둔 채 `Gemma 4`의 timeout/retry profile 차이가 repeatability와 품질에 어떤 영향을 주는지 확인합니다.

## 실행

1. compile
   - `python -m py_compile scripts/run_gemma_transport_model_comparison_check.py`
2. transport profile check
   - `python scripts/run_gemma_transport_model_comparison_check.py --experiment-id EXP-144 --repeat 3`

## 기대 결과

- `default_60s_no_retry`에서 보였던 timeout이 `90초/retry 1회` 또는 `120초/retry 1회`에서 줄어드는지 확인합니다.
- timeout이 줄더라도 strict region 품질까지 같이 유지되는지 확인합니다.

## 이번 실행 결과

- `default_60s_no_retry`
  - `success 2/3`
  - `timeout fail 1`
  - `avg_score 66.7`
- `timeout_90s_retry1`
  - `success 3/3`
  - `timeout fail 0`
  - `avg_score 97.8`
- `timeout_120s_retry1`
  - `success 3/3`
  - `timeout fail 0`
  - `avg_score 97.8`

## 판정

- `60초` transport profile이 실제 병목이라는 점은 확인됐습니다.
- `90초/retry 1회` 이상이면 timeout은 사라졌습니다.
- 다만 quality는 아직 `3/3 all pass`가 아니므로, transport 안정화와 baseline 승격은 분리해서 봐야 합니다.

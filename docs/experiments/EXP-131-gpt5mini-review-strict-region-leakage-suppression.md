# EXP-131 GPT-5 Mini Review Strict Region Leakage Suppression

## 목적

- `gpt-5-mini`가 `T04 review` strict baseline에서 반복적으로 내는 nearby-location leakage를 prompt constraint만으로 억제할 수 있는지 확인합니다.
- fallback model을 새로 찾지 못한 상황에서, 기존 접근 가능한 후보를 더 강하게 깎아 rescue 가능한지 봅니다.

## 변경 범위

- `services/worker/experiments/prompt_harness.py`
  - `EXP-131`을 추가했습니다.
  - baseline:
    - `review_translated_baseline_gpt5mini`
  - candidate:
    - `review_surface_locked_exact_region_anchor`

## 비교한 variant

- baseline
  - `review-translated` strict baseline prompt를 그대로 적용한 버전입니다.
- candidate
  - 위치 표현을 surface 단위로 더 강하게 잠근 버전입니다.
  - 핵심 제약:
    - `성수동` exact string은 정확히 1개 caption에만 허용
    - `#성수동`만 지역 hashtag로 허용
    - `서울숲`, `성수역`, `근처`, `인근`, `동네`, `핫플`, `앞` 같은 nearby/detail-location 표현은 모든 surface에서 금지
    - `product_name`, `review_quote`, `subText`에는 위치 단서를 절대 넣지 않고 맛/재방문 이유만 쓰도록 강제

## single run 결과

artifact:

- `docs/experiments/artifacts/exp-131-gpt-5-mini-review-strict-region-leakage-suppression.json`

주요 결과:

- baseline
  - `score=93.3`
  - 실패: `nearby location leaked into strict region budget`
  - hook: `한 번 먹고 기억나요`
  - cta: `방문해보세요`
- candidate
  - `score=100.0`
  - 실패 없음
  - hook: `한 번 먹고 기억나요`
  - cta: `방문해보세요`

## repeatability 결과

artifact:

- `docs/experiments/artifacts/exp-131-variant-repeatability.json`

주요 결과:

- baseline
  - `run_count=3`
  - `success_count=3`
  - `avg_score=93.3`
  - `all_runs_passed=false`
- candidate
  - `run_count=3`
  - `success_count=3`
  - `avg_score=100.0`
  - `all_runs_passed=true`
  - sample hooks:
    - `한 번 먹고 기억나`
    - `한 번 먹고 기억남`
    - `한 번 먹고 기억남`

## 해석

- 이번에는 `gpt-5-mini`를 더 이상 단순 tone reference로만 볼 필요는 없다는 신호가 나왔습니다.
- 기본 review-translated prompt에서는 strict region을 계속 깨지만, surface-lock까지 걸면 repeatability 기준에서도 `3/3 pass`가 나왔습니다.
- 즉 `gpt-5-mini`의 문제는 모델 자체보다 `review strict region policy를 충분히 surface-level로 명시하지 않았던 것`에 더 가까웠습니다.

## 판단

- `gpt-5-mini`는 `T04 review` strict baseline에서 rescue 가능합니다.
- 다만 조건이 있습니다.
  - 일반 review-translated prompt가 아니라
  - `review_surface_locked_exact_region_anchor` 수준의 강한 surface lock이 필요합니다.
- 따라서 다음 기준선은 이렇게 정리하는 편이 맞습니다.
  - `Gemma 4`: main baseline
  - `gpt-5-mini`: `review strict fallback candidate`, 단 `surface-locked prompt` 사용 시에만

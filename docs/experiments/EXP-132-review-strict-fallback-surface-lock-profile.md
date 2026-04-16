# EXP-132 Review Strict Fallback Surface Lock Profile

## 목적

- `EXP-131`에서 확인한 `gpt-5-mini surface-lock strict fallback`을 실험 메모가 아니라 baseline manifest option으로 승격합니다.
- 나중에 다시 실행할 때도 `--profile-id` 한 번으로 snapshot을 재현할 수 있게 합니다.

## 변경 범위

- `packages/template-spec/manifests/prompt-baseline-v1.json`
  - `baselineOptions[]`를 추가했습니다.
  - 새 profile:
    - `review_strict_fallback_surface_lock`
- `scripts/run_prompt_baseline_snapshot.py`
  - `--profile-id` 옵션을 추가했습니다.
  - 이제 top-level main baseline 외에도 manifest 안의 baseline option profile을 직접 snapshot할 수 있습니다.
  - `model_comparison` source뿐 아니라 `prompt_experiment` source도 읽을 수 있게 확장했습니다.
- `packages/template-spec/README.md`
  - prompt baseline manifest 안에 option profile이 들어간다는 점과 snapshot runner 사용 방식을 보강했습니다.

## 추가한 baseline option

- profile id
  - `review_strict_fallback_surface_lock`
- scope
  - `T04 review`
  - `b_grade_fun`
  - `regionName=성수동`
  - `detailLocation=서울숲 근처`
- selected model
  - `gpt-5-mini`
- selected prompt variant
  - `review_surface_locked_exact_region_anchor`
- role
  - `strict_fallback_candidate`

## snapshot 실행 결과

artifact:

- `docs/experiments/artifacts/exp-132-review-strict-fallback-surface-lock-snapshot.json`

주요 결과:

- acceptance
  - `accepted=true`
- score
  - `100.0`
- detail location leak count
  - `0`
- over-limit scene count
  - `0`
- hook
  - `한 번 먹고 기억남`
- cta
  - `방문해보기`

## 해석

- `EXP-131`에서 확인한 candidate가 실제로 snapshot 기준선까지 올라올 수 있다는 점을 확인했습니다.
- 즉 `gpt-5-mini`는 현재 기준에서 완전히 탈락한 secondary model이 아니라,
  - `T04 review`
  - `strict_all_surfaces`
  - `surface-locked exact region anchor`
  조건 아래에서는 재현 가능한 fallback profile입니다.

## 판단

- main baseline은 그대로 `Gemma 4 / T02 promotion`입니다.
- 다만 baseline manifest 안에 `review strict fallback` 옵션이 생겼으므로, 이후 운영 판단도 더 선명해집니다.
  - main baseline
    - `Gemma 4 / T02 promotion`
  - conditional fallback profile
    - `gpt-5-mini / T04 review / surface lock`

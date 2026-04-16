# EXP-129 Review Baseline Fallback Model Comparison

## 목적

- `T04 review`에서 이미 통과한 review-translated baseline prompt를 고정하고, `Gemma 4`와 `gpt-5-mini` 중 누가 실제 fallback 후보가 될 수 있는지 확인합니다.
- 품질 baseline과 운영 baseline을 분리해, `Gemma 4 timeout`이 있을 때 대체 모델이 strict policy를 유지할 수 있는지 봅니다.

## 변경 범위

- `services/worker/experiments/prompt_harness.py`
  - `EXP-129` model comparison definition을 추가했습니다.
  - 고정 prompt는 `fixed_review_baseline_transfer_translated`입니다.

## 고정 prompt 조건

- scenario
  - `T04 review`
  - `b_grade_fun`
  - `regionName=성수동`
  - `detailLocation=서울숲 근처`
- 고정 제약
  - `review_quote`, `product_name`은 12~14자 안팎
  - `cta`는 8~10자 안팎
  - `strict_all_surfaces` 위치 정책 유지
  - caption exact region 1회, 지역 hashtag 1개
  - nearby landmark 우회 표현 금지

## single run 결과

artifact:

- `docs/experiments/artifacts/exp-129-review-baseline-transfer-fallback-model-comparison.json`

주요 결과:

- deterministic reference
  - `score=93.3`
  - 실패: `region repeated more than allowed`
- Gemma 4
  - `score=100.0`
  - 실패 없음
  - hook: `한 입 먹고 바로 기억남`
  - cta: `저장하고 바로 가보셈`
- gpt-5-mini
  - `score=93.3`
  - 실패: `nearby location leaked into strict region budget`
  - leak surface: `captions`
  - 예시: `점심엔 여길? 서울숲 근처에서 든든하게`

## repeatability 결과

artifact:

- `docs/experiments/artifacts/exp-129-repeatability.json`

주요 결과:

- Gemma 4
  - `run_count=3`
  - `success_count=3`
  - `avg_score=100.0`
  - `all_runs_passed=true`
  - sample hooks:
    - `한 번 먹고 바로 기억나요`
    - `한 입 먹고 바로 기절함`
    - `한 번 먹고 바로 기억남`
- gpt-5-mini
  - `run_count=3`
  - `success_count=3`
  - `avg_score=93.3`
  - `all_runs_passed=false`
  - 3회 모두 nearby-location leakage가 재발했습니다.
  - leak surface는 주로 `captions`, 일부 run에서는 `subText`까지 번졌습니다.

## 해석

- `T04 review` 기준 fallback 판단은 이번에 꽤 분명하게 갈렸습니다.
- `Gemma 4`는 이번 scope에서 품질과 repeatability를 모두 통과했습니다.
- 반대로 `gpt-5-mini`는 timeout 문제는 없었지만, strict region policy를 반복적으로 깨서 fallback 기준선에는 못 미쳤습니다.
- 즉 review baseline에서 지금 병목은 `모델이 응답하느냐`보다 `strict_all_surfaces`를 끝까지 지키느냐`입니다.

## 판단

- 현재 `T04 review` 기준 main baseline은 계속 `Gemma 4`로 두는 편이 맞습니다.
- `gpt-5-mini`는 tone reference나 hook 아이디어 보조선으로는 쓸 수 있지만, strict review fallback model로 freeze하기에는 부족합니다.
- 다음 단계는 `Gemma 4 timeout 완화` 또는 `strict region을 지키는 다른 fallback 후보` 확인입니다.

# EXP-31 Local EXAONE 3.5 7.8B Prompt Lever Experiment - Promotion Region Repeat Constraint

## 1. 기본 정보

- 실험 ID: `EXP-31`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 EXAONE 프롬프트 레버 실험`

## 2. 왜 이 작업을 했는가

- `EXP-30` 결과를 보면 로컬 후보 중 `EXAONE 3.5 7.8B`가 한국어 자연스러움 면에서는 가장 유망했습니다.
- 하지만 `성수동` 반복이 심했고, 이 프로젝트의 지역 반복 정책을 어겼습니다.
- 따라서 먼저 `지역 반복 제약` 한 변수만 추가했을 때 실제로 반복이 줄어드는지 확인할 필요가 있었습니다.

## 3. baseline

### 고정한 조건

1. 시나리오: `T02 / promotion / b_grade_fun`
2. 모델: `ollama:exaone3.5:7.8b`
3. 자산: `규카츠`, `맥주` 실제 사진
4. 바뀐 변수: `slot_guidance`의 `region_repeat_constraint`만 변경

### 비교 대상

- deterministic reference
- baseline: `fixed_b_grade_tone_guidance_local_ollama`
- variant: `promotion_region_repeat_constraint_local_exaone`

## 4. 무엇을 바꿨는가

- `services/worker/experiments/prompt_harness.py`
  - `EXP-31` 정의 추가
  - baseline: local B급 tone guidance
  - variant: `지역명 총 2회 이하`, `본문 계열 최대 1회`, `benefit/urgency에는 지역명 반복 금지`
- `services/worker/tests/test_prompt_harness.py`
  - `EXP-31` 정의 테스트 추가

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-31-local-exaone-3-5-7-8b-prompt-lever-experiment-promotion-region-repeat-constraint.json`

### 결과 요약

- deterministic reference
  - score: `92.9`
  - region repeat count: `4`
- baseline `fixed_b_grade_tone_guidance_local_ollama`
  - score: `92.9`
  - region repeat count: `5`
  - over-limit scenes: `s1`, `s2`, `s3`
- variant `promotion_region_repeat_constraint_local_exaone`
  - score: `92.9`
  - region repeat count: `7`
  - over-limit scenes: `s1`, `s2`

### 확인된 것

1. 이번 레버는 성공하지 못했습니다.
2. baseline 대비 `over-limit scene` 수는 `3 -> 2`로 줄었지만, 정작 핵심 목표였던 `region repeat count`는 `5 -> 7`로 악화됐습니다.
3. `korean_integrity` 기준으로는 baseline/variant 모두 한글 깨짐 징후가 없었습니다.

## 6. 실패/제약

1. 로컬 `EXAONE 3.5 7.8B`는 이번 phrasing의 `지역 반복 제약`을 잘 따르지 않았습니다.
2. 제약 문장을 길게 추가할수록 오히려 caption과 hashtag에서 지역명이 더 늘어나는 반응이 나왔습니다.
3. 즉 현재 이 모델에는 `지역 반복 경고`보다 `짧은 output budget`이나 `hashtag rule` 쪽 제약이 더 잘 먹을 가능성이 큽니다.

## 7. 결론

- 가설 충족 여부: **실패**
- 판단:
  - `EXAONE 3.5 7.8B` 자체를 버릴 필요는 없습니다.
  - 다만 이 모델에서 첫 레버로 `region_repeat_constraint`를 고른 것은 맞지 않았습니다.
  - 다음에는 같은 모델을 유지한 채 `output constraint` 또는 `hashtag rule`로 가야 합니다.

## 8. 다음 액션

1. 다음은 `EXAONE 3.5 7.8B`를 고정하고 `output constraint` 한 레버를 봅니다.
2. 지역 반복은 그 다음 `hashtag rule`처럼 더 직접적인 제약으로 다시 분리합니다.

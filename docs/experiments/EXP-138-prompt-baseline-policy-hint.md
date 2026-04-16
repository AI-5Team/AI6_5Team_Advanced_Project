# EXP-138 Prompt Baseline Policy Hint

## 배경

- `EXP-137`까지 오면서 `promptBaselineSummary`는 단순 visibility를 넘어 `executionHint`와 `operationalChecks`를 포함하게 됐습니다.
- 하지만 실제 운영 판단 관점에서는 여전히 한 단계가 비어 있었습니다.
  - `executionHint.status=option_match`라고 해서 지금 바로 provider routing을 바꿔야 하는지
  - `coverage_gap`이면 자동 생성은 막아야 하는지, 아니면 수동 검토로 넘겨야 하는지
- 즉 "상태값"은 생겼지만, "이 상태를 어떻게 읽어야 하는지"가 summary 밖에 남아 있었습니다.

## 목표

1. `executionHint`를 그대로 두되, 그 위에 정책 해석 레이어 `policyHint`를 추가합니다.
2. `main baseline 참조`, `option profile 참조`, `수동 검토 필요`를 payload와 UI에서 같은 shape로 읽게 만듭니다.
3. 이번 단계도 실제 runtime provider routing 자동화는 하지 않고, 운영 판단 metadata까지만 확장합니다.

## 구현

### 1. contract 확장

- 파일: `packages/contracts/schemas/generation.ts`
- 추가 shape:
  - `PromptBaselinePolicyHint`
- `PromptBaselineSummary`에 `policyHint`를 추가했습니다.

### 2. worker runtime summary 확장

- 파일: `services/worker/pipelines/generation.py`
- `executionHint`를 입력으로 받아 `policyHint`를 파생하는 `_build_policy_hint()`를 추가했습니다.
- 정책 상태는 아래 3가지로 고정했습니다.
  - `main_reference`
  - `option_reference`
  - `coverage_gap`
- 추천 액션도 아래 3가지로 고정했습니다.
  - `use_main_profile_reference`
  - `use_option_profile_reference`
  - `manual_review_required`

### 3. web helper / UI 확장

- 파일:
  - `apps/web/src/lib/prompt-baseline.ts`
  - `apps/web/src/components/prompt-baseline-summary.tsx`
- web도 worker와 같은 규칙으로 `policyHint`를 구성하도록 맞췄습니다.
- UI에는 `PolicyHintCard`를 추가해 아래를 바로 보이게 했습니다.
  - 현재 policy state
  - 추천 액션
  - 수동 검토 필요 여부
  - 권장 profile / model / transport note 요약

## 결과

### worker smoke

- 기본 worker smoke는 여전히 `coverage_gap`입니다.
- 단, 이제는 이 결과가 단순 상태값이 아니라 아래처럼 해석됩니다.
  - `policyState=coverage_gap`
  - `recommendedAction=manual_review_required`
  - `requiresManualReview=true`

### API smoke

- `T01 new_menu / emphasizeRegion=true` 시나리오에서는 아래처럼 승격됐습니다.
  - `executionHint.status=option_match`
  - `policyHint.policyState=option_reference`
  - `policyHint.recommendedAction=use_option_profile_reference`

## 판단

1. 이번 단계로 `promptBaselineSummary`는 "무슨 profile이 맞는지"를 넘어서 "운영에서 어떻게 읽어야 하는지"까지 전달하게 됐습니다.
2. 그렇다고 아직 자동 라우팅 단계는 아닙니다.
3. 즉 현재 구조는 `coverage -> execution advisory -> policy interpretation`까지이며, 실제 provider routing 변경은 별도 결정으로 남겨두는 편이 맞습니다.

## 관련 파일

- `packages/contracts/schemas/generation.ts`
- `services/worker/pipelines/generation.py`
- `apps/web/src/lib/prompt-baseline.ts`
- `apps/web/src/components/prompt-baseline-summary.tsx`
- `services/worker/tests/test_generation_pipeline.py`
- `services/api/tests/test_api_smoke.py`

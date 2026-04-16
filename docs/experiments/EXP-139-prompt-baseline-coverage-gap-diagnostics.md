# EXP-139 Prompt Baseline Coverage Gap Diagnostics

## 배경

- `EXP-138`으로 `policyHint`까지 들어오면서, `coverage_gap`은 더 이상 숨겨진 상태가 아니라 payload/UI에서 바로 보이는 값이 됐습니다.
- 다만 그 상태만으로는 다음 액션이 부족했습니다.
  - exact match가 왜 안 났는지
  - 새 baseline option이 필요한지, 아니면 quick option 차이만 있는지
- 즉 `manual_review_required`라는 결론은 있었지만, "무엇이 달라서 manual review가 붙었는지"는 여전히 사람이 다시 비교해야 했습니다.

## 목표

1. exact match가 없을 때 `coverageHint`를 추가합니다.
2. 가장 가까운 profile이 무엇인지와 mismatch 축이 무엇인지 payload/UI에 같이 노출합니다.
3. 이 정보는 coverage gap 진단용이며, 추천 profile/policy 판단 자체를 바꾸지는 않습니다.

## 구현

### 1. contract 확장

- 파일: `packages/contracts/schemas/generation.ts`
- 추가 shape:
  - `PromptBaselineCoverageHint`
- `PromptBaselineSummary`에 `coverageHint`를 추가했습니다.

### 2. worker coverage 진단 추가

- 파일: `services/worker/pipelines/generation.py`
- 추가 helper:
  - `_collect_profile_mismatch_dimensions()`
  - `_build_coverage_hint()`
- 동작:
  - exact match가 있으면 `coverageHint = null`
  - exact match가 없으면 `default + option profiles` 중 가장 mismatch 수가 적은 profile을 nearest candidate로 선택
  - mismatch 축은 `purpose`, `templateId`, `styleId`, `quickOptions.*` 단위로 노출

### 3. web helper / UI 확장

- 파일:
  - `apps/web/src/lib/prompt-baseline.ts`
  - `apps/web/src/components/prompt-baseline-summary.tsx`
- web도 worker와 같은 로직으로 `coverageHint`를 계산하도록 맞췄습니다.
- UI에는 `CoverageHintCard`를 추가해 아래를 바로 보여주도록 했습니다.
  - nearest profile id
  - nearest profile kind
  - mismatch dimensions

## 결과

### worker smoke

- `T01 new_menu / friendly / quickOptions={}` 기본 smoke는 여전히 `coverage_gap`입니다.
- 하지만 이제 원인이 같이 드러납니다.
  - `nearestProfileId = new_menu_friendly_strict_region_anchor`
  - `nearestProfileKind = option`
  - `mismatchDimensions = ["quickOptions.emphasizeRegion"]`

### API smoke

- `T01 new_menu / emphasizeRegion=true` exact match 시나리오에서는
  - `recommendedProfile = new_menu_friendly_strict_region_anchor`
  - `coverageHint = null`
- 즉 진단은 coverage gap일 때만 붙고, exact match 상태를 흐리지 않도록 유지했습니다.

## 판단

1. 이번 단계로 `coverage_gap`는 단순 경고가 아니라, "다음 baseline 실험이 필요한 축"을 바로 읽을 수 있는 진단 정보가 됐습니다.
2. 특히 worker smoke처럼 `quickOptions.emphasizeRegion` 하나만 다른 경우, 새 연구선을 열지 않고도 gap 성격을 빠르게 파악할 수 있습니다.
3. 다음에 baseline option을 더 늘릴지 판단할 때도, 이제는 `coverageHint` 기준으로 gap이 구조적 미스매치인지 단일 옵션 차이인지 먼저 볼 수 있습니다.

## 관련 파일

- `packages/contracts/schemas/generation.ts`
- `services/worker/pipelines/generation.py`
- `apps/web/src/lib/prompt-baseline.ts`
- `apps/web/src/components/prompt-baseline-summary.tsx`
- `services/worker/tests/test_generation_pipeline.py`
- `services/api/tests/test_api_smoke.py`

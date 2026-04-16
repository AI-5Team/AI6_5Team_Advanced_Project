# EXP-140 Prompt Baseline Coverage Gap Action Classification

## 배경

- `EXP-139`로 `coverageHint`가 들어오면서, exact match가 없는 경우에도 nearest profile과 mismatch 축은 바로 볼 수 있게 됐습니다.
- 하지만 그 진단만으로는 아직 다음 액션이 자동으로 정리되지 않았습니다.
  - 이 gap이 새 option profile 후보인지
  - 새 scenario 실험이 필요한 gap인지
  - 아니면 우선 수동 검토로만 두는 편이 맞는지
- 즉 `coverage gap`도 진단 다음에 바로 이어지는 분류 단계가 한 칸 더 필요했습니다.

## 목표

1. `coverageHint`에 gap 분류와 추천 액션을 같이 추가합니다.
2. quick option 차이와 scenario 축 차이를 구분해 다음 실험 우선순위를 바로 읽을 수 있게 합니다.
3. 이 단계도 여전히 recommendation metadata 확장이며, 실제 runtime routing 자동화는 하지 않습니다.

## 구현

### 1. contract 확장

- 파일: `packages/contracts/schemas/generation.ts`
- `PromptBaselineCoverageHint`에 아래를 추가했습니다.
  - `gapClass`
  - `recommendedAction`

### 2. worker coverage gap 분류 추가

- 파일: `services/worker/pipelines/generation.py`
- `coverageHint` 생성 시 아래 규칙을 적용했습니다.
  - mismatch가 `quickOptions.*`만 있으면
    - `gapClass=quick_option_gap`
    - `recommendedAction=consider_option_profile`
  - mismatch에 `purpose/templateId/styleId`가 포함되면
    - `gapClass=scenario_gap`
    - `recommendedAction=run_new_scenario_experiment`
  - 그 외 혼합 mismatch는
    - `gapClass=mixed_gap`
    - `recommendedAction=keep_manual_review`

### 3. web helper / UI 확장

- 파일:
  - `apps/web/src/lib/prompt-baseline.ts`
  - `apps/web/src/components/prompt-baseline-summary.tsx`
- web도 worker와 같은 규칙으로 `gapClass`, `recommendedAction`을 계산하도록 맞췄습니다.
- `CoverageHintCard`에는 이제 아래가 같이 보입니다.
  - gap class
  - recommended action
  - nearest profile
  - mismatch dimensions

## 결과

### worker smoke

- `T01 new_menu / friendly / quickOptions={}` 기본 smoke는 여전히 `coverage_gap`입니다.
- 하지만 이제 그 성격이 아래처럼 더 명확해졌습니다.
  - `nearestProfileId = new_menu_friendly_strict_region_anchor`
  - `mismatchDimensions = ["quickOptions.emphasizeRegion"]`
  - `gapClass = quick_option_gap`
  - `recommendedAction = consider_option_profile`

### API smoke

- `T01 new_menu / emphasizeRegion=true` exact-match 시나리오에서는
  - `coverageHint = null`
- 즉 분류는 coverage gap 케이스에만 붙고, exact-match 상태를 덮지 않도록 유지했습니다.

## 판단

1. 이제 `coverageHint`는 단순 진단이 아니라, 다음 실험을 어떤 방향으로 열어야 하는지까지 같이 전달합니다.
2. 현재 worker smoke의 경우는 `scenario 전체가 어긋난 것`이 아니라 `quick option 축 하나가 비어 있는 것`으로 분류되므로, 새 scenario 실험보다 option profile 검토 쪽이 더 맞습니다.
3. 다음 단계에서 실제 실험 우선순위를 정할 때도, 이제 `gapClass` 기준으로 구조적 gap과 국소 option gap을 먼저 분리할 수 있습니다.

## 관련 파일

- `packages/contracts/schemas/generation.ts`
- `services/worker/pipelines/generation.py`
- `apps/web/src/lib/prompt-baseline.ts`
- `apps/web/src/components/prompt-baseline-summary.tsx`
- `services/worker/tests/test_generation_pipeline.py`
- `services/api/tests/test_api_smoke.py`

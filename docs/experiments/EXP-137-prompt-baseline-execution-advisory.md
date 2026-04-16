# EXP-137 Prompt Baseline Execution Advisory

## 배경

- `EXP-133`까지는 prompt baseline 정보가 payload/UI에 "보이는지"가 핵심이었습니다.
- `EXP-136`으로 `T01 new_menu` coverage candidate까지 manifest option profile로 들어왔지만, 아직 summary는 아래 수준에 머물러 있었습니다.
  - 어떤 profile이 exact match인지
  - 등록된 option profile이 무엇인지
- 실제 운영 판단에는 이 정도로는 부족했습니다.
- 지금 필요한 것은 `그래서 지금 어떤 profile/model을 참고해야 하는지`, `운영성 메모가 붙는지`를 한 단계 더 구조화하는 일이었습니다.

## 목표

1. `promptBaselineSummary` 안에 실행 권장 정보(`executionHint`)를 추가합니다.
2. manifest의 `operationalChecks[]`를 summary에 같이 실어, transport/retry 메모를 구조화합니다.
3. 이 정보는 여전히 recommendation metadata로만 유지하고, 실제 runtime routing 자동화와는 분리합니다.

## 구현

### 1. contract 확장

- 파일: `packages/contracts/schemas/generation.ts`
- 추가 shape:
  - `PromptBaselineExecutionHint`
  - `PromptBaselineOperationalCheckSummary`
  - `PromptBaselineTransportRecommendation`

### 2. manifest operational check 구조화

- 파일: `packages/template-spec/manifests/prompt-baseline-v1.json`
- `EXP-134` operational check에 아래를 추가했습니다.
  - `selectedModel`
  - `transportRecommendation`
- 목적:
  - prose 메모를 그대로 파싱하지 않고, runtime summary가 어떤 모델에 어떤 retry guard를 연결해야 하는지 읽을 수 있게 만들기 위함입니다.

### 3. worker runtime summary 확장

- 파일: `services/worker/pipelines/generation.py`
- `promptBaselineSummary`에 아래를 추가했습니다.
  - `executionHint`
  - `operationalChecks`
- 동작:
  - exact match profile이 있으면 `default_match` 또는 `option_match`
  - 없으면 `coverage_gap`
  - 권장 profile의 모델과 operational check의 모델이 맞으면 transport recommendation을 execution hint에 연결

### 4. web demo helper / UI 확장

- 파일:
  - `apps/web/src/lib/prompt-baseline.ts`
  - `apps/web/src/components/prompt-baseline-summary.tsx`
- UI에서 이제 아래를 바로 볼 수 있습니다.
  - 실행 권장 상태
  - 권장 profile / 권장 모델
  - transport guard 메모
  - 현재 컨텍스트에 적용 가능한 운영 메모

## 결과

### worker smoke

- `quickOptions={}`인 기본 worker smoke는 여전히 `coverage_gap`
- 즉 `profile coverage`와 `기본 deterministic smoke`를 혼동하지 않도록 유지했습니다.

### API smoke

- `T01 new_menu / emphasizeRegion=true` 시나리오에서는
  - `recommendedProfile = new_menu_friendly_strict_region_anchor`
  - `executionHint.status = option_match`
- 즉 기존 `visibility`가 실제로 `recommendation` 단계까지 한 칸 전진했습니다.

## 판단

1. 이번 단계는 runtime routing 자동화가 아니라, 운영 판단을 구조화한 recommendation metadata 확장입니다.
2. `profile / model / transport note`를 payload와 UI가 같은 shape로 읽게 됐다는 점이 핵심입니다.
3. 다음 단계에서 실제 routing을 붙이더라도, 이제는 어떤 기준을 따라야 하는지 summary shape가 먼저 정리된 상태입니다.

## 관련 파일

- `services/worker/pipelines/generation.py`
- `packages/contracts/schemas/generation.ts`
- `packages/template-spec/manifests/prompt-baseline-v1.json`
- `apps/web/src/lib/prompt-baseline.ts`
- `apps/web/src/components/prompt-baseline-summary.tsx`

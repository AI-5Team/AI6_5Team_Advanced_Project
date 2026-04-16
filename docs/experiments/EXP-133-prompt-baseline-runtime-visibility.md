# EXP-133 Prompt Baseline Runtime Visibility

## 배경

- `EXP-127`로 main prompt baseline을 freeze했습니다.
- `EXP-132`로 `T04 review` 전용 `gpt-5-mini surface-lock` fallback profile도 manifest option으로 승격했습니다.
- 하지만 이 기준선은 아직 문서/manifest 안에만 있었고, 실제 result payload나 web surface에서는 보이지 않았습니다.

## 목표

1. 현재 결과가 어떤 prompt baseline profile과 정렬되는지 `result` payload에서 바로 확인할 수 있게 합니다.
2. 이 정보가 실제 generation provider routing으로 오해되지 않도록 `recommendation only` 메타데이터로만 노출합니다.
3. worker, api, web demo fallback이 같은 shape를 보도록 맞춥니다.

## 구현

### 1. worker render meta 확장

- 파일: `services/worker/pipelines/generation.py`
- `manifests/prompt-baseline-v1.json`을 읽어 `promptBaselineSummary`를 계산합니다.
- summary에는 아래가 포함됩니다.
  - 현재 결과 context
    - `purpose`
    - `templateId`
    - `styleId`
    - `quickOptions`
  - `defaultProfile`
    - `main_baseline`
  - `recommendedProfile`
    - 현재 context와 exact match되는 profile
  - `candidateProfiles`
    - manifest의 `baselineOptions[]`
- 현재 runtime은 여전히 deterministic copy/render path이므로 `recommendationOnly=true`로 명시합니다.

### 2. API contract / response 확장

- 파일:
  - `packages/contracts/schemas/generation.ts`
  - `services/api/app/schemas/api.py`
  - `services/api/app/services/runtime.py`
- `ProjectResultResponse.promptBaselineSummary`를 추가했습니다.
- `/api/projects/{projectId}/result`에서 worker render meta의 값을 그대로 내려줍니다.

### 3. web demo fallback / UI 연결

- 파일:
  - `apps/web/src/lib/prompt-baseline.ts`
  - `apps/web/src/lib/demo-store.ts`
  - `apps/web/src/components/prompt-baseline-summary.tsx`
  - `apps/web/src/components/demo-workbench.tsx`
  - `apps/web/src/components/history-board.tsx`
- demo store도 같은 manifest를 읽어 `promptBaselineSummary`를 만들도록 맞췄습니다.
- workbench/result, history/result에서 아래를 확인할 수 있습니다.
  - 기본 baseline
  - 현재 결과 권장 profile
  - 조건부 option profile
  - model / preset / evidence experiment / location policy

## 결과 해석

### T01 / T03 / T04 일반 결과

- baseline manifest와 exact match되지 않으면 `recommendedProfile=null`로 표시됩니다.
- 이건 실패가 아니라, 현재 저장소에 등록된 prompt baseline profile coverage가 아직 좁다는 의미입니다.

### T02 promotion main baseline

- `T02 promotion / b_grade_fun / strict baseline` 결과는 `main_baseline`과 맞는지 바로 볼 수 있는 상태가 됐습니다.

### T04 review fallback profile

- `review_strict_fallback_surface_lock` 조건과 맞는 결과는 `recommendedProfile`로 드러날 수 있습니다.
- 이로써 `Gemma 4 main baseline`과 `gpt-5-mini conditional fallback`의 구분이 UI/payload 수준에서도 보입니다.

## 한계

1. 이 summary는 routing recommendation metadata입니다.
2. 현재 worker generation path가 자동으로 `Gemma 4`나 `gpt-5-mini`를 선택해 실행하는 것은 아닙니다.
3. exact match 기준은 현재 `purpose / templateId / styleId / quickOptions`까지만 봅니다.
4. 더 정교한 routing을 하려면 추후 runtime policy와 실제 generation provider selection을 별도로 연결해야 합니다.

## 판단

- 이번 단계는 baseline 연구 결과를 제품 surface에 연결하는 데 의미가 있습니다.
- 특히 `왜 이 결과가 baseline coverage 밖인지`, `어떤 fallback profile이 준비돼 있는지`를 팀이 공통 언어로 확인할 수 있게 됐습니다.
- 다만 아직은 `visibility` 단계이며, `runtime routing` 단계는 아닙니다.

## 관련 파일

- `services/worker/pipelines/generation.py`
- `services/api/app/services/runtime.py`
- `services/api/app/schemas/api.py`
- `packages/contracts/schemas/generation.ts`
- `apps/web/src/lib/prompt-baseline.ts`
- `apps/web/src/lib/demo-store.ts`
- `apps/web/src/components/prompt-baseline-summary.tsx`
- `apps/web/src/components/demo-workbench.tsx`
- `apps/web/src/components/history-board.tsx`

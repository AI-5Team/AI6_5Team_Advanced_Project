# EXP-141 Prompt Baseline Coverage Audit

## 배경

- `EXP-140`까지 오면서 각 개별 요청은 `executionHint / coverageHint / policyHint`로 해석할 수 있게 됐습니다.
- 하지만 아직 전체 baseline 구도가 얼마나 비어 있는지는 숫자로 보이지 않았습니다.
- 특히 `quick_option_gap`가 정말 반복되는지, 아니면 일부 예외만 그런지부터 확인할 필요가 있었습니다.

## 목표

1. 현재 manifest에 등록된 `main + option profiles`를 기준으로 coverage audit를 돌립니다.
2. 각 scenario context에서 quick option 8조합을 전수 점검해 `exact_match / coverage_gap / gapClass` 분포를 확인합니다.
3. audit 도중 드러나는 nearest-profile 선택 왜곡이 있으면 같이 보정합니다.

## 구현

### 1. coverage audit script 추가

- 파일: `scripts/run_prompt_baseline_coverage_audit.py`
- 동작:
  - manifest의 `selectedScenario`와 `baselineOptions[].selectedScenario`를 읽습니다.
  - 각 scenario context마다 `highlightPrice / shorterCopy / emphasizeRegion` 8조합을 전수 평가합니다.
  - 각 조합의 `recommendedProfileId`, `executionStatus`, `coverageHint`, `policyHint`를 artifact로 저장합니다.

### 2. nearest profile tie-break 보정

- 파일:
  - `services/worker/pipelines/generation.py`
  - `apps/web/src/lib/prompt-baseline.ts`
- audit를 돌려보니 `new_menu/T01/friendly`의 한 조합에서 quick option 차이만 있는 option profile 대신 `main_baseline`이 nearest profile로 선택되는 tie가 드러났습니다.
- 원인:
  - 기존 로직이 `mismatch 개수`만 보고 nearest profile을 고르다 보니, `구조 mismatch 3개`와 `quick option mismatch 3개`를 같은 것으로 취급했습니다.
- 수정:
  - nearest profile 선택 시 `purpose/template/style` 같은 구조 mismatch를 `quickOptions.*`보다 더 무겁게 보도록 우선순위를 바꿨습니다.
  - 결과적으로 동일한 개수의 mismatch라도, 구조가 맞는 profile이 먼저 선택되도록 정리했습니다.

### 3. 회귀 테스트 추가

- 파일: `services/worker/tests/test_generation_pipeline.py`
- 추가 검증:
  - `new_menu / T01 / friendly / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`
  - 위 케이스에서 nearest profile이 `main_baseline`이 아니라 `new_menu_friendly_strict_region_anchor`로 잡히는지 확인합니다.

## 결과

### coverage audit aggregate

- artifact: `docs/experiments/artifacts/exp-141-prompt-baseline-coverage-audit.json`
- 집계 결과:
  - `totalContexts = 24`
  - `default_match = 1`
  - `option_match = 2`
  - `coverage_gap = 21`
  - `quick_option_gap = 21`
  - `exact_match = 3`

### 해석

1. 현재 manifest coverage gap의 거의 전부는 `scenario 미정의`가 아니라 `quick option coverage 부족`입니다.
2. tie-break 보정 전에는 `new_menu` 한 케이스가 잘못 `scenario_gap`로 읽혔지만, 보정 후에는 그 케이스도 `quick_option_gap`로 정리됐습니다.
3. 즉 지금 baseline 확장의 다음 우선순위는 새 purpose/template 실험보다 quick option 축의 option profile 승격 기준을 정하는 쪽입니다.

## 판단

1. 현재 baseline coverage의 공백은 "시나리오를 새로 파야 하는 공백"보다 "기존 시나리오에 quick option 조합이 덜 채워진 공백"이 훨씬 큽니다.
2. 따라서 다음 액션은 무작정 새 scenario 실험을 늘리는 것이 아니라, `quick_option_gap`를 option profile로 승격할 기준을 세우는 일입니다.
3. 적어도 현재 manifest 상태에서는 `scenario_gap`보다 `quick_option_gap` 관리가 더 중요한 병목입니다.

## 관련 파일

- `scripts/run_prompt_baseline_coverage_audit.py`
- `services/worker/pipelines/generation.py`
- `apps/web/src/lib/prompt-baseline.ts`
- `services/worker/tests/test_generation_pipeline.py`
- `docs/experiments/artifacts/exp-141-prompt-baseline-coverage-audit.json`

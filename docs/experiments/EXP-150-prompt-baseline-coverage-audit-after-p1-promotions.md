# EXP-150 Prompt Baseline Coverage Audit After P1 Promotions

## 배경

- `EXP-147`, `EXP-149`까지 오면서 `promotion / shorterCopy=false`, `promotion / highlightPrice=false` 두 축이 모두 manifest option profile로 연결됐습니다.
- 하지만 실험을 두 건 더 성공시켰다고 해서 coverage가 얼마나 줄었는지는 자동으로 보이지 않습니다.
- 지금 필요한 것은 새 profile이 실제로 `coverage_gap`을 얼마나 줄였는지 다시 숫자로 확인하는 일입니다.

## 목표

1. 현재 manifest 상태로 prompt baseline coverage audit를 다시 돌립니다.
2. 이전 `EXP-141` 결과와 비교해 `option_match / coverage_gap` 변화량을 확인합니다.
3. promotion 축에서 무엇이 남았는지 다음 우선순위 관점으로 정리합니다.

## 구현

### 1. coverage audit script 확장

- 파일: `scripts/run_prompt_baseline_coverage_audit.py`
- 추가 내용:
  - `--experiment-id`
  - `--experiment-title`
- 목적:
  - 후속 audit artifact를 `EXP-141`과 섞지 않고 별도 experiment id로 기록하기 위함

## 실행

1. compile
   - `python -m py_compile scripts/run_prompt_baseline_coverage_audit.py`
2. audit
   - `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-150 --experiment-title "Prompt Baseline Coverage Audit After P1 Promotions" --artifact-name exp-150-prompt-baseline-coverage-audit-after-p1-promotions.json`

## 결과

### aggregate

- artifact:
  - `docs/experiments/artifacts/exp-150-prompt-baseline-coverage-audit-after-p1-promotions.json`

#### 이전 `EXP-141`

- `totalContexts = 24`
- `default_match = 1`
- `option_match = 2`
- `coverage_gap = 21`
- `exact_match = 3`

#### 현재 `EXP-150`

- `totalContexts = 24`
- `default_match = 1`
- `option_match = 4`
- `coverage_gap = 19`
- `exact_match = 5`

### 실제로 메워진 컨텍스트

1. `promotion / T02 / b_grade_fun / highlightPrice=false / shorterCopy=true / emphasizeRegion=false`
   - `promotion_surface_lock_highlight_price_off`
2. `promotion / T02 / b_grade_fun / highlightPrice=true / shorterCopy=false / emphasizeRegion=false`
   - `promotion_surface_lock_shorter_copy_off`

### 남은 promotion gap

- `highlightPrice=false / shorterCopy=false / emphasizeRegion=false`
  - nearest profile: `promotion_surface_lock_shorter_copy_off`
  - mismatch: `quickOptions.highlightPrice`
- `highlightPrice=false / shorterCopy=false / emphasizeRegion=true`
  - mismatch: `quickOptions.highlightPrice`, `quickOptions.emphasizeRegion`
- `highlightPrice=false / shorterCopy=true / emphasizeRegion=true`
  - nearest profile: `promotion_surface_lock_highlight_price_off`
  - mismatch: `quickOptions.emphasizeRegion`
- `highlightPrice=true / shorterCopy=false / emphasizeRegion=true`
  - nearest profile: `promotion_surface_lock_shorter_copy_off`
  - mismatch: `quickOptions.emphasizeRegion`
- `highlightPrice=true / shorterCopy=true / emphasizeRegion=true`
  - nearest profile: `main_baseline`
  - mismatch: `quickOptions.emphasizeRegion`

## 해석

1. 새 promotion option profile 2개는 실제로 coverage를 줄였습니다.
2. 전체 `coverage_gap`는 `21 -> 19`로 감소했고, `option_match`는 `2 -> 4`로 늘었습니다.
3. promotion 축은 이제 무작정 비어 있는 상태가 아니라,
   - `shorterCopy=false + highlightPrice=false` 조합 1건
   - `emphasizeRegion=true` 계열 3건
   - 그리고 전체 3토글 조합 1건
   정도만 남았습니다.

## 판단

- 이번 audit는 단순 재집계가 아니라, `P1` rescue가 실제로 coverage reduction으로 이어졌다는 근거입니다.
- 다음 기준선은 새 promotion option을 또 하나 더 파는지, 아니면 `new_menu/review`의 P2 single-toggle gap으로 넘어가는지 우선순위를 다시 정하는 일입니다.

## 결론

- `promotion` 기준으로는 가장 급한 공백 두 개가 실제로 메워졌습니다.
- 즉 현재 병목은 더 이상 "promotion 단일 토글 P1"이 아니라, `P2/P3` 재정렬입니다.

## 관련 파일

- `scripts/run_prompt_baseline_coverage_audit.py`
- `docs/experiments/artifacts/exp-150-prompt-baseline-coverage-audit-after-p1-promotions.json`

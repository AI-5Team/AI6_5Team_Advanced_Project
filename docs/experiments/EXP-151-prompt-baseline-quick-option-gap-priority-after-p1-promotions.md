# EXP-151 Prompt Baseline Quick Option Gap Priority After P1 Promotions

## 배경

- `EXP-150` audit로 `promotion` P1 두 축이 실제 coverage reduction으로 이어졌다는 점은 확인됐습니다.
- 그런데 기존 priority artifact(`EXP-142`)는 아직 rescue 이전 상태를 기준으로 정렬돼 있어서, 다음 우선순위를 그대로 믿으면 안 됩니다.
- 특히 option profile이 늘어난 뒤에는 `sourceProfileId` 기준 `P1/P2` 분류가 왜곡될 수 있어, priority band 계산 기준도 같이 정리할 필요가 있었습니다.

## 목표

1. 새 audit 결과(`EXP-150`)를 기준으로 quick option gap priority를 다시 계산합니다.
2. priority band가 현재 manifest 구조를 제대로 반영하도록 분류 기준을 보정합니다.
3. 다음으로 볼 `P2/P3` 후보를 다시 정렬합니다.

## 구현

### 1. priority script 보정

- 파일: `scripts/run_prompt_baseline_quick_option_gap_priority.py`
- 변경 내용:
  - `--experiment-id`
  - `--experiment-title`
  - `P1/P2` 판정을 `sourceProfileId`가 아니라 `coverageHint.nearestProfileKind / nearestProfileId` 기준으로 조정

### 2. 왜 보정이 필요했는가

- option profile이 늘어난 뒤에는 어떤 gap이 `main_baseline`에서 시작했더라도, 실제 nearest profile은 option일 수 있습니다.
- 이 상태에서 `sourceProfileId=main_baseline`만 보고 `P1`로 분류하면, 이미 option profile 인접 gap을 계속 `P1`로 오해하게 됩니다.
- 이번 보정은 "현재 가장 가까운 기준선이 무엇인가"를 기준으로 다시 밴드를 매기기 위한 것입니다.

## 실행

1. compile
   - `python -m py_compile scripts/run_prompt_baseline_quick_option_gap_priority.py`
2. priority refresh
   - `python scripts/run_prompt_baseline_quick_option_gap_priority.py --audit-artifact docs/experiments/artifacts/exp-150-prompt-baseline-coverage-audit-after-p1-promotions.json --experiment-id EXP-151 --experiment-title "Prompt Baseline Quick Option Gap Priority After P1 Promotions" --artifact-name exp-151-prompt-baseline-quick-option-gap-priority-after-p1-promotions.json`

## 결과

### aggregate

- artifact:
  - `docs/experiments/artifacts/exp-151-prompt-baseline-quick-option-gap-priority-after-p1-promotions.json`

#### 이전 `EXP-142`

- `P1 = 2`
- `P2 = 4`
- `P3 = 3`
- `P4 = 12`

#### 현재 `EXP-151`

- `P1 = 0`
- `P2 = 5`
- `P3 = 5`
- `P4 = 9`

### 현재 top candidate

1. `P2`
   - `promotion / T02 / b_grade_fun / highlightPrice=false / shorterCopy=false / emphasizeRegion=false`
   - nearest profile: `promotion_surface_lock_shorter_copy_off`
   - mismatch: `quickOptions.highlightPrice`
2. `P2`
   - `new_menu / T01 / friendly / highlightPrice=false / shorterCopy=true / emphasizeRegion=true`
   - mismatch: `quickOptions.shorterCopy`
3. `P2`
   - `new_menu / T01 / friendly / highlightPrice=true / shorterCopy=false / emphasizeRegion=true`
   - mismatch: `quickOptions.highlightPrice`
4. `P2`
   - `review / T04 / b_grade_fun / highlightPrice=false / shorterCopy=false / emphasizeRegion=false`
   - mismatch: `quickOptions.shorterCopy`
5. `P2`
   - `review / T04 / b_grade_fun / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`
   - mismatch: `quickOptions.highlightPrice`

## 해석

1. 이제 `promotion`에는 더 이상 `P1`이 남아 있지 않습니다.
2. 남은 최상위 후보는 `option profile` 인접 단일 토글들입니다.
3. `promotion`에서는 `highlightPrice=false + shorterCopy=false` 조합이 가장 앞에 왔고, 그 다음은 `new_menu`, `review`의 단일 토글 두 쌍입니다.
4. `emphasizeRegion` 단일 토글은 여전히 `P3`로 남아 있으므로, location policy 리스크 때문에 한 단계 뒤에서 보는 편이 맞습니다.

## 판단

- 이번 priority refresh는 단순 재정렬이 아니라, 다음 실험 대상을 다시 정의한 결과입니다.
- 즉 앞으로의 우선순위는 `promotion 잔여 P2 1건 -> new_menu/review P2 -> emphasizeRegion P3 -> 다중 토글 P4` 순서로 보는 편이 맞습니다.

## 결론

- `P1` 단계는 실질적으로 종료됐습니다.
- 다음 실험은 `promotion / highlightPrice=false / shorterCopy=false / emphasizeRegion=false`를 option-adjacent P2로 다루는 것이 가장 자연스럽습니다.

## 관련 파일

- `scripts/run_prompt_baseline_quick_option_gap_priority.py`
- `docs/experiments/artifacts/exp-151-prompt-baseline-quick-option-gap-priority-after-p1-promotions.json`
- `docs/experiments/artifacts/exp-150-prompt-baseline-coverage-audit-after-p1-promotions.json`

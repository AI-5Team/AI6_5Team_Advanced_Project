# EXP-142 Prompt Baseline Quick Option Gap Priority

## 배경

- `EXP-141` coverage audit로 현재 manifest coverage gap 21건이 전부 `quick_option_gap`라는 사실까지는 확인했습니다.
- 하지만 그 다음 단계로는 어떤 gap부터 실제 option profile 승격 후보로 볼지 우선순위가 필요했습니다.
- 지금 필요한 것은 gap을 더 찾는 것이 아니라, 이미 드러난 21건을 작게 쪼개서 다음 실험 순서를 정하는 일입니다.

## 목표

1. `quick_option_gap` 21건을 바로 실행 가능한 우선순위 밴드로 나눕니다.
2. 가장 작은 변경으로 baseline coverage를 넓히는 후보를 맨 앞으로 올립니다.
3. location policy 리스크가 큰 `emphasizeRegion` 단일 토글과 다중 토글 조합은 뒤로 미룹니다.

## 구현

### 1. priority script 추가

- 파일: `scripts/run_prompt_baseline_quick_option_gap_priority.py`
- 입력:
  - `docs/experiments/artifacts/exp-141-prompt-baseline-coverage-audit.json`
- 출력:
  - `docs/experiments/artifacts/exp-142-prompt-baseline-quick-option-gap-priority.json`

### 2. priority band 규칙

- `P1`
  - `main_baseline` 인접
  - 단일 quick option gap
  - `emphasizeRegion` 미포함
- `P2`
  - 기존 option profile 인접
  - 단일 quick option gap
  - `emphasizeRegion` 미포함
- `P3`
  - 단일 quick option gap
  - `emphasizeRegion` 포함
- `P4`
  - 다중 quick option 조합 gap

## 결과

### aggregate

- `totalQuickOptionGaps = 21`
- `P1 = 2`
- `P2 = 4`
- `P3 = 3`
- `P4 = 12`

### top priority candidates

1. `P1`
   - `promotion / T02 / b_grade_fun / highlightPrice=false / shorterCopy=true / emphasizeRegion=false`
   - mismatch: `quickOptions.highlightPrice`
2. `P1`
   - `promotion / T02 / b_grade_fun / highlightPrice=true / shorterCopy=false / emphasizeRegion=false`
   - mismatch: `quickOptions.shorterCopy`
3. `P2`
   - `new_menu / T01 / friendly / highlightPrice=false / shorterCopy=true / emphasizeRegion=true`
   - mismatch: `quickOptions.shorterCopy`
4. `P2`
   - `new_menu / T01 / friendly / highlightPrice=true / shorterCopy=false / emphasizeRegion=true`
   - mismatch: `quickOptions.highlightPrice`
5. `P2`
   - `review / T04 / b_grade_fun / highlightPrice=false / shorterCopy=false / emphasizeRegion=false`
   - mismatch: `quickOptions.shorterCopy`
6. `P2`
   - `review / T04 / b_grade_fun / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`
   - mismatch: `quickOptions.highlightPrice`

### 해석

1. 가장 먼저 볼 후보는 `main_baseline` 주변의 단일 토글 2건입니다.
2. 그 다음은 이미 option profile이 있는 `new_menu`, `review` 시나리오에서 단일 토글만 비어 있는 4건입니다.
3. `emphasizeRegion` 단일 토글 3건은 location policy 리스크가 더 크므로 한 단계 뒤로 미루는 편이 맞습니다.
4. 다중 토글 12건은 단일 토글 coverage를 먼저 채운 뒤 보더라도 늦지 않습니다.

## 판단

1. 다음 실험 우선순위는 `P1 -> P2 -> P3 -> P4` 순서가 가장 합리적입니다.
2. 즉 가장 먼저 해야 할 일은 `promotion/T02` 기준으로 `highlightPrice only`, `shorterCopy only` 두 gap이 실제 option profile 승격 가치가 있는지 확인하는 것입니다.
3. 이 결과가 나오기 전까지는 `emphasizeRegion` 계열이나 다중 토글 조합으로 바로 넘어갈 이유가 약합니다.

## 관련 파일

- `scripts/run_prompt_baseline_quick_option_gap_priority.py`
- `docs/experiments/artifacts/exp-142-prompt-baseline-quick-option-gap-priority.json`
- `docs/experiments/artifacts/exp-141-prompt-baseline-coverage-audit.json`

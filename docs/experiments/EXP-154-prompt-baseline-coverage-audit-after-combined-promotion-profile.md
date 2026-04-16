# EXP-154 Prompt Baseline Coverage Audit After Combined Promotion Profile

## 배경

- `EXP-153`까지 오면서 promotion의 combined non-region gap도 option profile로 연결됐습니다.
- 이 시점에는 다시 coverage audit를 돌려, promotion 공백이 실제로 얼마나 줄었는지 숫자로 확인하는 편이 맞습니다.

## 목표

1. combined promotion profile까지 반영한 manifest 상태로 coverage audit를 다시 돌립니다.
2. 직전 `EXP-150` 결과와 비교해 변화량을 확인합니다.
3. promotion 축에서 무엇만 남았는지 정리합니다.

## 실행

1. `python scripts/run_prompt_baseline_coverage_audit.py --experiment-id EXP-154 --experiment-title "Prompt Baseline Coverage Audit After Combined Promotion Profile" --artifact-name exp-154-prompt-baseline-coverage-audit-after-combined-promotion-profile.json`

## 결과

- artifact:
  - `docs/experiments/artifacts/exp-154-prompt-baseline-coverage-audit-after-combined-promotion-profile.json`

### `EXP-150` 대비 변화

- `option_match = 4 -> 5`
- `coverage_gap = 19 -> 18`
- `exact_match = 5 -> 6`

### promotion 축 상태

- option match:
  - `highlightPrice=false / shorterCopy=false / emphasizeRegion=false`
  - `highlightPrice=false / shorterCopy=true / emphasizeRegion=false`
  - `highlightPrice=true / shorterCopy=false / emphasizeRegion=false`
- default match:
  - `highlightPrice=true / shorterCopy=true / emphasizeRegion=false`
- 남은 공백:
  - `emphasizeRegion=true`가 포함된 4조합만 남음

## 해석

1. combined promotion profile은 실제 coverage를 한 칸 더 줄였습니다.
2. promotion 축은 이제 non-region 공백이 사실상 정리됐고, 남은 것은 `emphasizeRegion=true` 계열뿐입니다.

## 판단

- promotion 다음 우선순위는 non-region이 아니라 `region emphasis` 또는 다른 purpose의 P2입니다.

## 결론

- 이제 prompt baseline 확장의 다음 초점은 promotion non-region gap이 아니라, `new_menu/review` P2 또는 `promotion emphasizeRegion=true`입니다.

## 관련 파일

- `scripts/run_prompt_baseline_coverage_audit.py`
- `docs/experiments/artifacts/exp-154-prompt-baseline-coverage-audit-after-combined-promotion-profile.json`

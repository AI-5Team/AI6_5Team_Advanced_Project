# EXP-143 Promotion Highlight Price Off Coverage Comparison

## 배경

- `EXP-142` priority 결과에서 가장 먼저 볼 후보는 `promotion / T02 / b_grade_fun`의 단일 토글 2건이었습니다.
- 그중 첫 번째는 `highlightPrice=false / shorterCopy=true / emphasizeRegion=false` 조건입니다.
- 이 후보는 `main_baseline`과 같은 scenario를 유지하면서 가격 강조만 끄는 가장 작은 변화라서, 실제 option profile 승격 가능성을 먼저 확인할 가치가 있었습니다.

## 목표

1. `T02 promotion` strict anchor baseline 원칙을 유지한 채 `highlightPrice=false` 조건을 실험합니다.
2. `Gemma 4`와 `gpt-5-mini` 중 누가 이 single-toggle gap을 coverage 후보로 만들 수 있는지 비교합니다.
3. single run뿐 아니라 repeatability까지 보고, 실제 option profile 승격 가능성을 판단합니다.

## 구현

### 1. scenario 추가

- 파일: `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-restaurant-promotion-b-grade-real-photo-highlight-price-off`
  - `purpose=promotion`
  - `templateId=T02`
  - `styleId=b_grade_fun`
  - `quickOptions={ highlightPrice=false, shorterCopy=true, emphasizeRegion=false }`

### 2. model comparison 정의 추가

- 파일: `services/worker/experiments/prompt_harness.py`
- 추가 실험:
  - `EXP-143`
  - `fixed_promotion_strict_anchor_no_price_highlight`
- 핵심 제약:
  - strict anchor baseline 구조 유지
  - `highlightPrice=false`일 때 가격 숫자/할인폭을 hook, benefit, urgency의 주제로 앞세우지 않음
  - 혜택이 있더라도 가격보다 메뉴 강점, 방문 이유를 먼저 보이게 함

## 실행

1. single run
   - `python scripts/run_model_comparison_experiment.py --experiment-id EXP-143`
2. repeatability
   - `python scripts/run_prompt_repeatability_spot_check.py --experiment-id EXP-143 --repeat 3 --model-names models/gemma-4-31b-it,gpt-5-mini`

## 결과

### single run

- artifact:
  - `docs/experiments/artifacts/exp-143-promotion-strict-anchor-highlight-price-off-coverage-comparison.json`

#### Gemma 4

- score: `100.0`
- failed checks: 없음
- hook:
  - `오늘 안 오면 손해인가요?`
- cta:
  - `방문해서 확인하기`

#### GPT-5 Mini

- score: `86.7`
- failed checks:
  - `region appears in fewer than required areas`
  - `nearby location leaked into strict region budget`
- hook:
  - `오늘만 규카츠·맥주 찬스?`
- cta:
  - `방문`

### repeatability

- artifact:
  - `docs/experiments/artifacts/exp-143-repeatability.json`

#### Gemma 4

- `success_count = 0 / 3`
- 세 번 모두 `The read operation timed out`
- 즉 품질 repeatability를 보기 전에 transport 단계에서 막혔습니다.

#### GPT-5 Mini

- `success_count = 3 / 3`
- `avg_score = 86.7`
- `all_runs_passed = false`
- 즉 응답은 안정적이지만 strict baseline coverage 후보로는 품질이 부족했습니다.

## 판단

1. 이 후보는 아직 option profile로 승격할 수 없습니다.
2. 이유는 두 갈래입니다.
   - `Gemma 4`: single run 품질은 통과했지만 repeatability에서 transport timeout 3/3
   - `gpt-5-mini`: 응답은 안정적이지만 location policy / region anchor 품질이 부족
3. 따라서 `highlightPrice=false`는 현재 기준으로 `main baseline adjacent P1` 후보이긴 하지만, 이번 증거만으로는 manifest option 추가를 정당화하지 못합니다.

## 결론

- `promotion / T02 / highlightPrice=false`는 `실험 완료, 승격 보류` 상태로 두는 편이 맞습니다.
- 다음 P1 후보는 `shorterCopy=false / highlightPrice=true / emphasizeRegion=false` 쪽으로 넘어가는 것이 더 생산적입니다.

## 관련 파일

- `services/worker/experiments/prompt_harness.py`
- `docs/experiments/artifacts/exp-143-promotion-strict-anchor-highlight-price-off-coverage-comparison.json`
- `docs/experiments/artifacts/exp-143-repeatability.json`

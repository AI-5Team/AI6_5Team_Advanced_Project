# EXP-144 Promotion Shorter Copy Off Coverage Comparison

## 배경

- `EXP-142` priority 결과에서 `P1` 후보는 2건이었고, 첫 번째 `highlightPrice=false` 후보는 `EXP-143`에서 승격에 실패했습니다.
- 두 번째 `P1` 후보는 `promotion / T02 / b_grade_fun / highlightPrice=true / shorterCopy=false / emphasizeRegion=false` 조건입니다.
- 이 후보는 가격 강조는 유지하되 `shorterCopy`만 끄는 단일 토글이라서, `main_baseline` 주변 coverage를 가장 작은 비용으로 넓힐 수 있는지 확인할 가치가 있었습니다.

## 목표

1. `T02 promotion` strict anchor baseline 원칙을 유지한 채 `shorterCopy=false` 조건을 실험합니다.
2. `Gemma 4`와 `gpt-5-mini` 중 누가 이 single-toggle gap을 coverage 후보로 만들 수 있는지 비교합니다.
3. single run뿐 아니라 repeatability까지 보고, 실제 option profile 승격 가능성을 판단합니다.

## 구현

### 1. scenario 추가

- 파일: `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-restaurant-promotion-b-grade-real-photo-shorter-copy-off`
  - `purpose=promotion`
  - `templateId=T02`
  - `styleId=b_grade_fun`
  - `quickOptions={ highlightPrice=true, shorterCopy=false, emphasizeRegion=false }`

### 2. model comparison 정의 추가

- 파일: `services/worker/experiments/prompt_harness.py`
- 추가 실험:
  - `EXP-144`
  - `fixed_promotion_strict_anchor_no_shorter_copy`
- 핵심 제약:
  - strict anchor baseline 구조 유지
  - `shorterCopy=false`일 때 primaryText는 계속 짧게 유지하되, 필요한 설명은 subText/caption으로 넘김
  - 가격, 할인, 세트 이점은 숨기지 않되 여러 surface에 반복하지 않음

## 실행

1. compile
   - `python -m py_compile services/worker/experiments/prompt_harness.py`
2. single run
   - `python scripts/run_model_comparison_experiment.py --experiment-id EXP-144`
3. repeatability
   - `python scripts/run_prompt_repeatability_spot_check.py --experiment-id EXP-144 --repeat 3 --model-names models/gemma-4-31b-it,gpt-5-mini`

## 결과

### single run

- artifact:
  - `docs/experiments/artifacts/exp-144-promotion-strict-anchor-shorter-copy-off-coverage-comparison.json`

#### Gemma 4

- score: `100.0`
- failed checks: 없음
- hook:
  - `오늘 안 오면 손해인가요?`
- cta:
  - `예약하고 방문하기`

#### GPT-5 Mini

- score: `86.7`
- failed checks:
  - `region appears in fewer than required areas`
  - `nearby location leaked into strict region budget`
- hook:
  - `오늘 안 오면 손해?`
- cta:
  - `방문`

### repeatability

- artifact:
  - `docs/experiments/artifacts/exp-144-repeatability.json`

#### Gemma 4

- `success_count = 0 / 3`
- 세 번 모두 `The read operation timed out`
- 즉 single-run 품질은 통과했지만, repeatability를 검증할 만큼 transport가 안정적이지 않았습니다.

#### GPT-5 Mini

- `success_count = 3 / 3`
- `avg_score = 86.7`
- `all_runs_passed = false`
- sample hooks:
  - `오늘 안 오면 손해?`
  - `오늘 안 오면 손해?`
  - `오늘만 규카츠 할인?`

## 판단

1. 이 후보도 아직 option profile로 승격할 수 없습니다.
2. 이유는 `EXP-143`과 동일한 두 갈래입니다.
   - `Gemma 4`: single run 품질은 통과했지만 repeatability에서 transport timeout 3/3
   - `gpt-5-mini`: 응답은 안정적이지만 location policy / region anchor 품질이 부족
3. 즉 `P1` top candidate 2건을 모두 확인했지만, 현재 모델 조합만으로는 `promotion / T02`의 인접 quick option gap을 승격 가능한 baseline으로 고정하지 못했습니다.

## 결론

- `promotion / T02 / shorterCopy=false`는 `실험 완료, 승격 보류` 상태로 두는 편이 맞습니다.
- 이제 바로 다음 우선순위는 `P2` 후보로 내려가거나, `Gemma 4` transport 안정성 자체를 별도 축으로 다루는 것입니다.
- 단순히 같은 `P1` 유형을 더 늘리기보다, 왜 single-run winner가 repeatability에서 쓰러지는지와 왜 `gpt-5-mini`가 strict region anchor에서 계속 미끄러지는지를 분리해 다루는 편이 낫습니다.

## 관련 파일

- `services/worker/experiments/prompt_harness.py`
- `docs/experiments/artifacts/exp-144-promotion-strict-anchor-shorter-copy-off-coverage-comparison.json`
- `docs/experiments/artifacts/exp-144-repeatability.json`

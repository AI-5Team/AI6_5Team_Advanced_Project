# EXP-130 Review Strict Fallback Candidate Sweep

## 목적

- `T04 review` strict baseline prompt를 고정한 상태에서, 현재 접근 가능한 후보 중 누가 `Gemma 4`의 fallback이 될 수 있는지 확인합니다.
- 이번에는 `Gemma 4`, `gpt-4.1-mini`, `gpt-5-mini`를 같은 조건으로 비교합니다.

## 변경 범위

- `services/worker/experiments/prompt_harness.py`
  - `EXP-130` model comparison definition을 추가했습니다.
  - OpenAI Responses 요청 body를 모델별로 조금 다르게 보내도록 호환성 패치를 넣었습니다.
    - `reasoning.effort`는 `gpt-5` 계열에만 전송
    - `text.verbosity`는 `gpt-5` 계열에만 `low`, 그 외는 `medium`
- `scripts/run_prompt_repeatability_spot_check.py`
  - `--model-names` 옵션을 추가해 repeatability 대상 모델을 직접 고를 수 있게 했습니다.

## 고정 조건

- scenario
  - `T04 review`
  - `b_grade_fun`
  - `regionName=성수동`
  - `detailLocation=서울숲 근처`
- fixed prompt
  - `fixed_review_baseline_transfer_translated`
- 비교 모델
  - `models/gemma-4-31b-it`
  - `gpt-4.1-mini`
  - `gpt-5-mini`

## 실행 결과

artifact:

- `docs/experiments/artifacts/exp-130-review-strict-fallback-candidate-sweep.json`

주요 결과:

- deterministic reference
  - `score=93.3`
  - 실패: `region repeated more than allowed`
- Gemma 4
  - `score=100.0`
  - 실패 없음
  - hook: `한 번 먹으면 계속 생각남`
  - cta: `저장하고 방문하기`
- gpt-5-mini
  - `score=93.3`
  - 실패: `nearby location leaked into strict region budget`
  - hook: `한 번 먹고 기억나요`
  - cta: `방문해보세요`
- gpt-4.1-mini
  - 품질 비교까지 가지 못했습니다.
  - request shape 호환성 패치 전에는 `reasoning.effort`, `text.verbosity` 제약으로 막혔습니다.
  - 패치 후에는 실제 근본 원인이 `403 model_not_found`로 드러났습니다.
  - 즉 현재 project access 기준으로는 `gpt-4.1-mini` 자체가 실험 불가 상태입니다.

## 해석

- 현재 계정/프로젝트 기준에서 review strict fallback 후보는 실질적으로 다시 두 갈래만 남습니다.
  - `Gemma 4`
  - `gpt-5-mini`
- 이 둘 중 strict baseline 통과 여부는 여전히 `Gemma 4`만 pass입니다.
- `gpt-5-mini`는 응답 속도는 좋지만 nearby-location leakage가 계속 남습니다.
- `gpt-4.1-mini`는 품질 이전에 access가 없어서 active 후보군에 넣을 수 없습니다.

## 판단

- 이번 sweep으로 `strict review fallback 후보를 넓혀 보자`는 시도는 일단 막혔습니다.
- 이유는 두 가지입니다.
  - `gpt-5-mini`: policy 품질 미달
  - `gpt-4.1-mini`: project access 부재
- 따라서 다음 자연스러운 축은 새 모델을 더 늘리는 것보다,
  - `Gemma 4 timeout 완화`
  - `gpt-5-mini leakage 억제 prompt/constraint`
  - 또는 access 가능한 다른 후보 확인
  중 하나입니다.

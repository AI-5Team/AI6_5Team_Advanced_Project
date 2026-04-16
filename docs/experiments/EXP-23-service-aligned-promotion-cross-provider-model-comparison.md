# EXP-23 Service-Aligned Promotion Cross-Provider Model Comparison

## 1. 기본 정보

- 실험 ID: `EXP-23`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `모델 비교 실험 하네스`, `cross-provider model-only comparison`

## 2. 왜 이 작업을 했는가

- 지금까지 prompt 실험이 사실상 `Gemma 4` 단일 모델에 고정돼 있었습니다.
- 사용자 요청대로, 프롬프트를 고정한 채 모델만 바꾸는 비교 경로가 필요했습니다.
- 다만 실제 환경을 확인해 보니 `OPENAI_API_KEY`는 존재하지만 유효하지 않았고, 이 제약 자체도 실험 기록으로 남길 필요가 있었습니다.

## 3. baseline

### 고정한 조건

1. 시나리오: `T02 / promotion / b_grade_fun / 실제 음식 사진`
2. 프롬프트: `EXP-15`에서 효과가 좋았던 `B급 tone guidance`
3. 바뀐 변수: `모델`만 변경

### 비교 대상

- deterministic reference
- `models/gemma-4-31b-it`
- `gpt-5-mini`
- `gpt-4.1-mini`

## 4. 무엇을 바꿨는가

- `services/worker/experiments/prompt_harness.py`
  - provider-agnostic model dispatcher 추가
  - `openai` provider 지원 추가
  - `EXP-23` cross-provider model comparison 정의 추가
  - provider별 기본 key env resolver 추가
  - 실패 모델도 artifact에 기록되도록 failure-tolerant model comparison runner 추가
  - 에러 메시지에 key 일부가 남지 않도록 sanitization 추가
- `scripts/run_model_comparison_experiment.py`
  - model-only comparison 실행 스크립트 추가
- `services/worker/tests/test_prompt_harness.py`
  - model comparison 정의와 provider env resolver 테스트 추가

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-23-service-aligned-promotion-cross-provider-model-comparison.json`

### 확인된 것

1. `Gemma 4`는 같은 고정 prompt에서 실제 응답을 정상 생성했습니다.
2. 현재 환경의 `OPENAI_API_KEY`는 존재하지만 유효하지 않아, `gpt-5-mini`, `gpt-4.1-mini` 모두 `401 invalid_api_key`로 실패했습니다.
3. 즉, cross-provider 비교 하네스는 생겼지만 현재 머신 상태로는 `OpenAI` 쪽 실험 재현이 막혀 있습니다.

### 수치 요약

- deterministic reference
  - score: `92.9`
- `models/gemma-4-31b-it`
  - score: `92.9`
  - hook: `미친 육즙 규카츠, 오늘만 이 가격!`
  - cta: `지금 바로 방문하기`
- `gpt-5-mini`
  - 실행 실패: `401 invalid_api_key`
- `gpt-4.1-mini`
  - 실행 실패: `401 invalid_api_key`

## 6. 실패/제약

1. `OPENAI_API_KEY`는 저장소에서 넣은 값이 아니라 머신 환경변수였지만, 실제로는 유효하지 않았습니다.
2. 이번 실험은 cross-provider 비교 구조를 만들고 실패 상태를 분리 기록하는 데는 성공했지만, OpenAI 결과 품질 비교까지는 진행되지 못했습니다.
3. 현재 시점에서 cross-provider 실제 비교는 key 정상화가 선행돼야 합니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `Gemma 4`에 고정되지 않는 model comparison 구조는 마련됐습니다.
  - 하지만 현재 환경의 OpenAI key 제약 때문에 cross-provider 품질 비교는 보류 상태입니다.

## 8. 다음 액션

1. OpenAI key가 정상화되면 `EXP-23`을 재실행해 실제 cross-provider 비교를 완성합니다.
2. 그 전까지는 실행 가능한 Google family 비교를 우선 진행합니다.

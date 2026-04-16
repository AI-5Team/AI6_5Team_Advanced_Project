# EXP-24 Service-Aligned Promotion Google Model Comparison

## 1. 기본 정보

- 실험 ID: `EXP-24`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `Google family model-only comparison`

## 2. 왜 이 작업을 했는가

- `EXP-23`에서 cross-provider 비교 하네스는 만들었지만, OpenAI key가 유효하지 않아 실제 비교가 막혔습니다.
- 영상 생성 본선으로 넘어가기 전에, 지금 당장 실행 가능한 범위에서 `Gemma 4` 외 다른 모델 비교는 계속 진행해도 된다는 사용자 방향에 맞춰 Google family 비교를 별도로 수행했습니다.

## 3. baseline

### 고정한 조건

1. 시나리오: `T02 / promotion / b_grade_fun / 실제 음식 사진`
2. 프롬프트: `EXP-15`에서 효과가 좋았던 `B급 tone guidance`
3. 바뀐 변수: `모델`만 변경

### 비교 대상

- deterministic reference
- `models/gemma-4-31b-it`
- `models/gemini-2.5-flash`
- `models/gemini-2.5-flash-lite`

## 4. 무엇을 바꿨는가

- `services/worker/experiments/prompt_harness.py`
  - `EXP-24` Google model comparison 정의 추가
- `services/worker/tests/test_prompt_harness.py`
  - Google family comparison definition 테스트 추가

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-24-service-aligned-promotion-google-model-comparison.json`

### 결과 요약

- deterministic reference
  - score: `92.9`
  - 문제: 지역 반복 초과, scene text 과긴
- `models/gemma-4-31b-it`
  - score: `92.9`
  - 장점: scene 길이는 안정적
  - 제약: 지역 반복 초과는 여전히 남음
- `models/gemini-2.5-flash`
  - 실행 실패: `invalid JSON response`
  - 의미: 카피 내용 이전에 output format 안정성이 약했음
- `models/gemini-2.5-flash-lite`
  - score: `92.9`
  - 장점: 응답 속도 가장 빠름
  - 제약: 모든 scene가 text budget 초과

### 확인된 것

1. 같은 prompt라도 모델별 실패 양상이 다릅니다.
2. `Gemma 4`는 output format과 scene budget 측면에서 가장 안정적이었습니다.
3. `Gemini 2.5 Flash`는 JSON format 안정성 문제가 드러났습니다.
4. `Gemini 2.5 Flash-Lite`는 빠르지만 길이 제약이 가장 약했습니다.

## 6. 실패/제약

1. `Gemini 2.5 Flash`는 아예 JSON을 끝까지 닫지 못해 비교 score가 아닌 format failure로 탈락했습니다.
2. `Gemini 2.5 Flash-Lite`는 속도는 좋았지만 render-readiness 기준에서는 가장 불리했습니다.
3. 이번 비교도 단일 실행 1회라 재현성은 더 봐야 합니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - “Gemma 4만 보지 말자”는 방향 자체는 맞습니다.
  - 다만 현재 실행 가능한 Google family 범위에서 보면, `Gemma 4`는 속도보다 안정성 쪽에서 여전히 강합니다.
  - 즉 `Gemma 4 확정`이 아니라, 현재 기준으로는 `Gemma 4 = 안정성 baseline`, `Gemini Flash 계열 = 속도/형식 리스크 후보`로 보는 게 더 정확합니다.

## 8. 다음 액션

1. 다음 model 비교는 `review(T04)` 축으로도 한 번 더 확인합니다.
2. 동시에 `Gemini 2.5 Flash`의 JSON format failure를 줄이기 위한 output constraint 레버를 따로 분리 실험합니다.

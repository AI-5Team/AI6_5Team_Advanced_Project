# EXP-26 Service-Aligned Review Model Comparison

## 1. 기본 정보

- 실험 ID: `EXP-26`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `review model-only comparison`

## 2. 왜 이 작업을 했는가

- 우선순위를 다시 정리한 결과, `Gemini 2.5 Flash` 형식 안정화보다 먼저 해야 할 일은 `T04 review`에서도 실제 후보 모델이 일반화되는지 확인하는 것이었습니다.
- `T02 promotion`에서는 `gpt-5-mini`가 후보로 살아났지만, 서비스는 템플릿별로 결과가 달라질 수 있으므로 `review` 축 검증이 필요했습니다.

## 3. baseline

### 고정한 조건

1. 시나리오: `T04 / review / b_grade_fun / 실제 음식 사진(라멘)`
2. 프롬프트: `EXP-18`에서 확인했던 `region repeat constraint`
3. 바뀐 변수: `모델`만 변경

### 비교 대상

- deterministic reference
- `models/gemma-4-31b-it`
- `gpt-5-mini`

## 4. 무엇을 바꿨는가

- `services/worker/experiments/prompt_harness.py`
  - `EXP-26` review model comparison 정의 추가
- `services/worker/tests/test_prompt_harness.py`
  - `EXP-26` 정의 테스트 추가

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-26-service-aligned-review-model-comparison.json`

### 결과 요약

- deterministic reference
  - score: `92.9`
  - 문제: 지역 반복 초과, scene 길이 초과
- `models/gemma-4-31b-it`
  - score: `92.9`
  - 장점: scene 길이는 안정적
  - 제약: `ctaText lacks explicit action keyword`
  - 예: `지금 바로 면치러 가기`
- `gpt-5-mini`
  - score: `100.0`
  - 장점: evaluation failed check 없음, 응답 속도 빠름
  - 제약:
    - `s1` 길이 초과
    - `s2` primary/secondary 반복
    - scene-plan closing CTA는 actionable false

### 확인된 것

1. `review(T04)`에서는 `gpt-5-mini`가 문장 규칙 면에서는 더 잘 맞았습니다.
2. 하지만 `scene-plan` 기준으로 보면 `gpt-5-mini`도 아직 render-ready라고 보긴 어렵습니다.
3. `Gemma 4`는 길이 안정성은 좋지만 CTA 행동 단어 쪽이 약했습니다.
4. 즉 `review` 축에서는 promotion 때보다 model 우열이 더 단순하지 않습니다.

## 6. 실패/제약

1. 현재 evaluation score는 copy rule 중심이라 `scene-plan 문제`를 충분히 벌점으로 반영하지 못합니다.
2. 그래서 `gpt-5-mini`는 score `100.0`이지만 실제로는 render-readiness 문제가 남아 있습니다.
3. 이번 비교도 단일 실행 1회라 재현성은 더 봐야 합니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `gpt-5-mini`는 `review`에서도 후보로 남습니다.
  - 하지만 바로 baseline 확정은 어렵고, `output constraint`를 붙여 scene budget과 반복을 먼저 줄여야 합니다.
  - `Gemma 4`는 아직 버릴 모델은 아니며, CTA 행동성 보강이 필요합니다.

## 8. 다음 액션

1. 다음 실험은 `gpt-5-mini`를 고정하고 `output constraint` 한 레버만 추가합니다.
2. 그 다음 `Gemini 2.5 Flash`의 JSON/format 안정화 실험을 진행합니다.
3. 이후 Hugging Face token을 활용한 오픈소스 비교 경로를 붙입니다.

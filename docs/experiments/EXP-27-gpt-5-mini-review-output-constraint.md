# EXP-27 GPT-5 Mini Review Output Constraint

## 1. 기본 정보

- 실험 ID: `EXP-27`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `gpt-5-mini` prompt lever experiment, `T04 review` render-readiness 개선

## 2. 실험 목적

- `EXP-26` 결과를 보면 `gpt-5-mini`는 review 템플릿에서 score는 높았지만 scene 길이 초과, 반복, CTA 안정성 문제가 남았습니다.
- 그래서 이번에는 `gpt-5-mini`를 고정하고, **render-ready output constraint 한 가지**만 추가해 문제를 줄일 수 있는지 확인했습니다.

## 3. baseline 조건 고정

| 항목 | 고정값 |
|---|---|
| 모델 | `gpt-5-mini` |
| provider | OpenAI Responses API |
| 업종 | `restaurant` |
| 목적 | `review` |
| 스타일 | `b_grade_fun` |
| 지역 | `성수동` |
| 상세 위치 | `서울숲 근처` |
| 템플릿 | `T04` |
| 자산 세트 | `docs/sample/음식사진샘플(라멘).jpg` |
| quick options | `highlightPrice=false`, `shorterCopy=true`, `emphasizeRegion=false` |
| 평가 기준 | copy bundle 규칙 점수 + `scene-plan` 길이/중복/actionable 지표 |

## 4. 이번에 바꾼 레버

- baseline prompt:
  - `EXP-18`에서 사용한 `region repeat constraint`
- variant prompt:
  - 위 baseline 유지
  - 여기에 `render-ready output constraint` 한 블록만 추가
    - `review_quote`, `product_name` 길이 제한
    - `cta`는 행동 단어로 시작
    - `subText`는 primaryText 반복 금지

## 5. 수행 절차

1. `EXP-27`을 `T04 review` 시나리오에 추가했습니다.
2. `gpt-5-mini`를 고정한 채 baseline prompt와 output constraint variant를 각각 실행했습니다.
3. artifact를 아래 경로에 저장했습니다.
   - `docs/experiments/artifacts/exp-27-gpt-5-mini-prompt-lever-experiment-review-output-constraint.json`

## 6. 결과 요약

### 정량 요약

| 케이스 | copy score | over-limit scene | repeated scene | closing CTA actionable | 비고 |
|---|---:|---:|---:|---:|---|
| deterministic reference | `92.9` | `2` | `0` | `true` | 지역 반복 초과 |
| gpt-5-mini baseline | `92.9` | `1` | `0` | `true` | CTA keyword heuristic 실패 |
| gpt-5-mini output constraint | `100.0` | `0` | `0` | `true` | 실패 체크 없음 |

### baseline 대비 차이

| 비교 항목 | gpt-5-mini baseline | gpt-5-mini output constraint |
|---|---|---|
| hookText | `한입에 반한 국물, 힐링 라멘!` | `한입에 반한 진한 국물!` |
| ctaText | `지금 바로 맛보러 가기` | `방문해보기` |
| over-limit scene | `s1` | 없음 |
| repeated scene | 없음 | 없음 |
| failed checks | `ctaText lacks explicit action keyword` | 없음 |

## 7. 관찰 내용

### 확인된 것

1. `gpt-5-mini`에서는 `output constraint`가 실제로 유효한 레버였습니다.
2. 동일 모델, 동일 템플릿에서 길이/반복/CTA 제약을 추가하자 `scene-plan` 안정성과 copy score가 함께 좋아졌습니다.
3. 즉 `review` 축의 다음 병목은 모델보다 `output constraint` 쪽이라는 점이 더 분명해졌습니다.

### 아직 모르는 것

1. `방문해보기` CTA가 충분히 강한지, 혹은 너무 약한지는 별도 평가가 필요합니다.
2. 이 constraint가 `promotion` 템플릿에도 그대로 일반화되는지는 아직 모릅니다.

## 8. 실패/제약

1. 이번 variant는 좋아졌지만, CTA의 표현 강도 자체는 아직 다듬을 여지가 있습니다.
2. 단일 실행 1회입니다.

## 9. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `review(T04)`에서는 지금 단계에서 `gpt-5-mini output constraint`가 가장 우선순위 높은 개선 레버였습니다.
  - 다음으로 넘어갈 수 있는 기준선이 생겼습니다.

## 10. 다음 액션

1. 다음은 `Gemini 2.5 Flash`에서 JSON/format 안정화가 실제로 가능한지 다시 확인합니다.
2. 이후 Hugging Face token 기반 오픈소스 비교 경로를 붙입니다.

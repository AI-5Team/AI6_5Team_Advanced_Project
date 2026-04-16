# EXP-28 Gemini 2.5 Flash Strict JSON Output Constraint

## 1. 기본 정보

- 실험 ID: `EXP-28`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `Gemini 2.5 Flash` prompt lever experiment, format 안정화

## 2. 실험 목적

- 이전 비교에서 `Gemini 2.5 Flash`는 내용 품질 이전에 JSON format failure가 먼저 발생했습니다.
- 그래서 이번에는 `Gemini 2.5 Flash`를 고정하고, **strict JSON output constraint 한 가지**만 추가해 형식 실패를 줄일 수 있는지 확인했습니다.

## 3. baseline 조건 고정

| 항목 | 고정값 |
|---|---|
| 모델 | `models/gemini-2.5-flash` |
| provider | Google Generative Language API |
| 업종 | `restaurant` |
| 목적 | `promotion` |
| 스타일 | `b_grade_fun` |
| 지역 | `성수동` |
| 상세 위치 | `서울숲 근처` |
| 템플릿 | `T02` |
| 자산 세트 | `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg` |
| quick options | `highlightPrice=true`, `shorterCopy=true`, `emphasizeRegion=false` |
| 평가 기준 | JSON parse 성공 여부 + copy bundle 규칙 점수 + `scene-plan` 지표 |

## 4. 이번에 바꾼 레버

- baseline prompt:
  - `B급 tone guidance`
- variant prompt:
  - 위 baseline 유지
  - 여기에 `strict JSON output constraint` 한 블록만 추가
    - JSON 외 설명문 금지
    - 코드펜스 금지
    - 마지막 중괄호까지 완결
    - 필수 키 1회만 출력

## 5. 수행 절차

1. `EXP-28`을 `T02 promotion` 시나리오에 추가했습니다.
2. `Gemini 2.5 Flash`를 고정한 채 baseline prompt와 strict JSON variant를 각각 실행했습니다.
3. artifact를 아래 경로에 저장했습니다.
   - `docs/experiments/artifacts/exp-28-gemini-2-5-flash-prompt-lever-experiment-strict-json-output-constraint.json`

## 6. 결과 요약

### 정량 요약

| 케이스 | copy score | 결과 |
|---|---:|---|
| deterministic reference | `92.9` | 정상 |
| Gemini 2.5 Flash baseline | `0.0` | `invalid JSON response` |
| Gemini 2.5 Flash strict JSON constraint | `0.0` | `invalid JSON response` |

### baseline 대비 차이

| 비교 항목 | Gemini baseline | Gemini strict JSON constraint |
|---|---|---|
| JSON parse | 실패 | 실패 |
| 응답 길이 | 짧게 끊김 | 짧게 끊김 |
| 개선 여부 | 없음 | 없음 |

## 7. 관찰 내용

### 확인된 것

1. `Gemini 2.5 Flash`는 prompt에 JSON 제약을 더 써도 이번 조건에서는 format failure가 그대로 남았습니다.
2. 즉 지금 단계에서는 단순 프롬프트 레버 하나만으로 이 모델의 형식 안정성을 구하기 어렵습니다.
3. 이 문제는 프롬프트보다 provider/model 특성 또는 응답 truncation 쪽 가능성이 더 커 보입니다.

### 아직 모르는 것

1. `maxOutputTokens`, 자산 수, prompt 길이를 더 줄이면 살아나는지는 아직 모릅니다.
2. `Flash-Lite`나 다른 오픈소스 경로와 비교했을 때 이 문제가 얼마나 구조적인지도 아직 미확인입니다.

## 8. 실패/제약

1. baseline과 variant 모두 JSON parse 단계에서 실패했습니다.
2. 따라서 이번 실험은 품질 비교가 아니라 `형식 안정화 실패 기록`에 가깝습니다.
3. 단일 실행 1회입니다.

## 9. 결론

- 가설 충족 여부: **미충족**
- 판단:
  - `Gemini 2.5 Flash`는 현재 조건에서 우선순위를 올리기 어렵습니다.
  - 지금 당장은 `gpt-5-mini`나 `Gemma 4`처럼 이미 usable한 모델을 먼저 다듬는 편이 맞습니다.

## 10. 다음 액션

1. 다음은 Hugging Face token 기반 오픈소스 비교 경로를 붙입니다.
2. `Gemini 2.5 Flash`는 나중에 prompt 길이/자산 수/토큰 수 축으로 다시 봅니다.

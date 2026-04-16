# EXP-18 Review Region Repeat Constraint

## 1. 기본 정보

- 실험 ID: `EXP-18`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `Gemma 4` prompt lever experiment, `T04 review` 지역 반복 제어

## 2. 실험 목적

- `EXP-16`, `EXP-17` 결과를 보면 `T04 review`의 다음 핵심 병목은 `지역 반복`이었습니다.
- 그래서 이번에는 **slot guidance 한 가지**만 바꿔, 지역명을 어디에 몇 번까지 쓸지 더 직접적으로 명시했습니다.

## 3. baseline 조건 고정

| 항목 | 고정값 |
|---|---|
| 모델 | `models/gemma-4-31b-it` |
| provider | Google Generative Language API |
| 온도 | `0.2` |
| 업종 | `restaurant` |
| 목적 | `review` |
| 스타일 | `b_grade_fun` |
| 지역 | `성수동` |
| 상세 위치 | `서울숲 근처` |
| 템플릿 | `T04` |
| 자산 세트 | `docs/sample/음식사진샘플(라멘).jpg` |
| quick options | `highlightPrice=false`, `shorterCopy=true`, `emphasizeRegion=false` |
| 평가 기준 | copy bundle 규칙 점수 + `scene-plan` 길이/중복 지표 |

## 4. 이번에 바꾼 레버

- baseline prompt:
  - 공통 compact slot guidance
- variant prompt:
  - 지역명은 `hookText`, captions, hashtags를 합쳐 총 2회 이하
  - 해시태그에 이미 지역명이 들어가면 본문 계열에서는 최대 1회만 허용
  - `review_quote`, `product_name`에는 지역명을 억지로 반복하지 않기

## 5. 수행 절차

1. `EXP-18`을 `T04 review` 시나리오에 추가했습니다.
2. baseline prompt와 `review region repeat constraint` variant를 각각 실행했습니다.
3. artifact를 아래 경로에 저장했습니다.
   - `docs/experiments/artifacts/exp-18-gemma-4-prompt-lever-experiment-review-region-repeat-constraint.json`

## 6. 결과 요약

### 정량 요약

| 케이스 | copy score | region repeat | over-limit scene | 비고 |
|---|---:|---:|---:|---|
| deterministic reference | `92.9` | `4` | `2` | 지역 반복 초과 |
| Gemma baseline prompt | `85.7` | `3` | `0` | 지역 반복 초과 + CTA heuristic 실패 |
| Gemma review region repeat constraint | `100.0` | `2` | `0` | 실패 체크 없음 |

### baseline 대비 차이

| 비교 항목 | Gemma baseline prompt | Gemma review region repeat constraint |
|---|---|---|
| hookText | `성수동에서 찾은 인생 라멘, 안 먹으면 평생 후회!` | `국물 한 입에 극락 갑니다!!` |
| 지역 반복 | `3회` | `2회` |
| review_quote/product_name | 이미 길이는 안정적 | 길이 유지하면서 지역 반복만 줄임 |
| CTA | `지금 바로 달려가기` | `지금 바로 확인하기` |
| failed checks | 지역 반복 초과, CTA heuristic 실패 | 없음 |

## 7. 관찰 내용

### 확인된 것

1. `T04 review`에서는 `지역 반복 제약`이 실제로 유의미한 레버였습니다.
2. 같은 모델, 같은 자산, 같은 템플릿에서 지역 반복을 더 직접적으로 명시하자 `region repeat 3 -> 2`로 줄었습니다.
3. 길이 안정성은 유지하면서 정책 위반만 제거할 수 있었습니다.

### 아직 모르는 것

1. 이 결과가 단일 실행 우연인지 반복 실행에서도 유지되는지는 아직 모릅니다.
2. `확인하기` CTA가 실제 서비스 톤에 충분히 강한지는 아직 별도 검토가 필요합니다.

## 8. 실패/제약

1. baseline prompt 결과가 실행마다 다소 흔들려 단일 실행 비교에는 변동성이 있습니다.
2. CTA heuristic은 colloquial 표현을 여전히 보수적으로 평가합니다.
3. 단일 실행 1회입니다.

## 9. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `T04 review`에서는 `B급 tone guidance`보다 `지역 반복 제약`이 더 우선순위가 높은 레버로 보입니다.
  - 즉, 템플릿별로 잘 먹는 레버가 다르다는 점이 더 분명해졌습니다.

## 10. 다음 액션

1. 다음 `review` 실험은 `CTA 강도`를 한 레버로 봅니다.
2. 이후 `T02 promotion`과 `T04 review`의 우선 레버 차이를 비교 표로 정리합니다.

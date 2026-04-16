# EXP-16 Service-Aligned B-Grade Review Tone

## 1. 기본 정보

- 실험 ID: `EXP-16`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `Gemma 4` prompt lever experiment, `T04 review` 일반화 검증

## 2. 실험 목적

- `EXP-15`에서 `B급 tone guidance`가 `T02 promotion`에는 유효했습니다.
- 이번에는 같은 레버를 `T04 review`에 옮겨도 같은 효과가 유지되는지 확인했습니다.
- 즉, **바뀐 것은 `audience_guidance` 하나뿐**이고, 템플릿/목적만 `review`로 고정했습니다.

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
  - 스타일 기본값만 따르고 추가 후기 톤 지시는 없음
- variant prompt:
  - `B급 감성 리뷰 = 친구가 바로 보내는 한 줄 제보`
  - `review_quote`는 짧고 말맛 있게
  - `product_name`은 메뉴 장점이 한 번에 보이게
  - `cta`는 저장/방문/재방문 같은 행동 단어를 앞쪽에 두기

## 5. 수행 절차

1. `EXP-16` 시나리오를 `T04 / review / b_grade_fun / 라멘 사진` 기준으로 추가했습니다.
2. baseline prompt와 `B급 review tone guidance` variant를 각각 실행했습니다.
3. artifact를 아래 경로에 저장했습니다.
   - `docs/experiments/artifacts/exp-16-gemma-4-prompt-lever-experiment-service-aligned-b-grade-review-tone.json`

## 6. 결과 요약

### 정량 요약

| 케이스 | copy score | over-limit scene | closing CTA actionable | 비고 |
|---|---:|---:|---:|---|
| deterministic reference | `92.9` | `2` | `true` | 지역 반복 초과 |
| Gemma baseline prompt | `100.0` | `1` | `false` | 실패 체크 없음 |
| Gemma B급 review tone guidance | `92.9` | `0` | `true` | 지역 반복 초과 |

### baseline 대비 차이

| 비교 항목 | Gemma baseline prompt | Gemma B급 review tone guidance |
|---|---|---|
| review_quote | `국물 한 모금에 전생이 기억났습니다` | `국물 한 입에 극락 감` |
| product_name | `영혼까지 채우는 라멘` | `육즙 폭발 인생 라멘` |
| CTA | `당장 입성하기` / `지금 바로 확인하기` | `저장하고 당장 방문` / `저장하고 이번 주말에 바로 방문하세요!` |
| 지역 반복 | `2회` | `3회` |
| 길이 예산 | `s1` 초과 | 초과 없음 |

## 7. 관찰 내용

### 확인된 것

1. `B급 tone guidance`는 `T04 review`에서도 문장을 더 짧고 전단지형으로 만드는 효과는 있었습니다.
2. 특히 `review_quote`, `product_name`, `cta`의 scene-plan 길이 예산은 더 잘 지켰습니다.
3. 하지만 `T04 review`에서는 같은 레버가 지역 반복을 오히려 늘려 정책 위반을 만들었습니다.

### 아직 모르는 것

1. 이 결과가 단일 실행 우연인지 반복 실행에서도 유지되는지는 아직 모릅니다.
2. `review` 템플릿에서는 B급 톤보다 다른 레버가 더 중요할 가능성이 있습니다.

## 8. 실패/제약

1. `T04 review`에서는 `B급 tone guidance`가 `T02`만큼 보편적으로 좋지 않았습니다.
2. action heuristic은 `확인하기` 같은 표현을 아직 보수적으로 평가합니다.
3. 단일 실행 1회 결과입니다.

## 9. 결론

- 가설 충족 여부: **부분 실패**
- 판단:
  - `B급 tone guidance`는 `promotion`에는 강했지만 `review`에는 그대로 일반화되지 않았습니다.
  - 따라서 다음 `review` 실험은 톤 자체보다 `길이 제약`, `지역 반복 제약`, `CTA 표현` 쪽을 우선 보는 것이 더 합리적입니다.

## 10. 다음 액션

1. `T04 review`에서는 `slot 길이 제한`을 한 레버로 분리해 확인합니다.
2. 그 다음 `지역 반복 제약` 또는 `CTA 강도`를 분리해 봅니다.

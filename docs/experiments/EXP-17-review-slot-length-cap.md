# EXP-17 Review Slot Length Cap

## 1. 기본 정보

- 실험 ID: `EXP-17`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `Gemma 4` prompt lever experiment, `T04 review` 길이 예산 제어

## 2. 실험 목적

- `EXP-16` 결과 `T04 review`에서 가장 뚜렷한 병목은 톤 자체보다 `quote 길이`였습니다.
- 그래서 이번에는 **slot guidance 한 가지**만 바꿔 `review_quote`, `product_name`, `cta` 길이를 명시적으로 제한했습니다.

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
  - `review_quote`: 12자 안팎
  - `product_name`: 12자 안팎
  - `cta`: 10자 안팎
  - `subText`: primary보다 더 짧거나 같은 길이

## 5. 수행 절차

1. `EXP-17`을 `T04 review` 시나리오에 추가했습니다.
2. baseline prompt와 `review slot length cap` variant를 각각 실행했습니다.
3. artifact를 아래 경로에 저장했습니다.
   - `docs/experiments/artifacts/exp-17-gemma-4-prompt-lever-experiment-review-slot-length-cap.json`

## 6. 결과 요약

### 정량 요약

| 케이스 | copy score | over-limit scene | closing CTA actionable | 비고 |
|---|---:|---:|---:|---|
| deterministic reference | `92.9` | `2` | `true` | 지역 반복 초과 |
| Gemma baseline prompt | `92.9` | `1` | `false` | CTA 액션성 heuristic 실패 |
| Gemma review slot length cap | `85.7` | `0` | `false` | 지역 반복 초과 + CTA 액션성 heuristic 실패 |

### baseline 대비 차이

| 비교 항목 | Gemma baseline prompt | Gemma review slot length cap |
|---|---|---|
| hookText | `한 입 먹고 기절할 뻔한 썰 푼다` | `인생 라멘 찾았다... 진짜 미쳤음` |
| review_quote 길이 | 과김, `s1` 초과 | 길이 예산 안으로 수렴 |
| product_name 길이 | 안정적 | 안정적 |
| CTA | `지금 바로 달려가기` | `지금 바로 저장하고 가보자` |
| 지역 반복 | 허용 범위 | 초과 |

## 7. 관찰 내용

### 확인된 것

1. `slot 길이 제한`은 실제로 `scene-plan` 과긴 문구를 줄였습니다.
2. 하지만 길이만 강하게 제약하면 지역 반복과 CTA 표현이 다른 쪽으로 튈 수 있습니다.
3. 즉, `T04 review`에서는 길이 제약 단독 레버만으로는 전체 품질을 올리기 어렵습니다.

### 아직 모르는 것

1. `길이 제약 + 지역 반복 제약`을 같이 묶으면 좋아질 가능성은 있지만, 아직 이번 원칙상 섞지 않았습니다.
2. CTA heuristic이 colloquial B급 표현을 얼마나 잘 반영하는지도 더 검토가 필요합니다.

## 8. 실패/제약

1. 지역 반복 제약을 별도로 주지 않아 오히려 region repeat가 늘었습니다.
2. `가보자`, `달려가기` 같은 colloquial CTA는 현 heuristic에서 보수적으로 잡힙니다.
3. 단일 실행 1회입니다.

## 9. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `slot 길이 제한`은 render-readiness 측면에서는 유효합니다.
  - 하지만 copy policy 전체 품질까지 올리려면 다음에는 `지역 반복 제약` 또는 `CTA 행동성`을 별도 레버로 다시 봐야 합니다.

## 10. 다음 액션

1. 다음 `review` 실험은 `지역 반복 제약`을 한 레버로 봅니다.
2. 그 다음은 `CTA 강도`를 한 레버로 분리합니다.

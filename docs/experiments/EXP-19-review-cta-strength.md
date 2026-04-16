# EXP-19 Review CTA Strength

## 1. 기본 정보

- 실험 ID: `EXP-19`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `Gemma 4` prompt lever experiment, `T04 review` CTA 행동성 강화

## 2. 실험 목적

- `EXP-18`까지 보면 `review` 템플릿의 다음 병목은 `CTA 표현`이었습니다.
- 그래서 이번에는 **slot guidance 한 가지**만 바꿔 `cta`, `ctaText`의 행동성을 더 직접적으로 지시했습니다.

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
  - `cta`, `ctaText`는 감탄사보다 행동 단어를 먼저 둔다
  - `저장`, `방문`, `확인`, `예약` 중 최소 하나를 포함한다
  - `가보자`, `달려가기`보다 `저장하기`, `방문하기`, `지금 확인` 같은 표현을 우선한다

## 5. 실험 중 수정한 평가 기준

- 1차 실행에서 `저장하기`가 CTA action으로 인정되지 않는 평가 버그를 확인했습니다.
- 조치:
  - action keyword에 `저장`을 추가
  - 관련 테스트 추가 후 재실행

즉, 이번 결과는 위 평가 문제를 바로잡은 뒤 재실행한 최종 결과입니다.

## 6. 수행 절차

1. `EXP-19`를 `T04 review` 시나리오에 추가했습니다.
2. baseline prompt와 `review CTA strength` variant를 각각 실행했습니다.
3. artifact를 아래 경로에 저장했습니다.
   - `docs/experiments/artifacts/exp-19-gemma-4-prompt-lever-experiment-review-cta-strength.json`

## 7. 결과 요약

### 정량 요약

| 케이스 | copy score | region repeat | closing CTA actionable | 비고 |
|---|---:|---:|---:|---|
| deterministic reference | `92.9` | `4` | `true` | 지역 반복 초과 |
| Gemma baseline prompt | `92.9` | `2` | `true` | CTA 표현이 흐림 |
| Gemma review CTA strength | `100.0` | `2` | `true` | 실패 체크 없음 |

### baseline 대비 차이

| 비교 항목 | Gemma baseline prompt | Gemma review CTA strength |
|---|---|---|
| hookText | `인생 라멘 발견, 이건 진짜 반칙이지!` | `인생 라멘 발견!` |
| CTA | `지금 바로 달려가기` | `지금 저장하기` |
| 행동성 | colloquial하지만 흐림 | 짧고 직접적 |
| failed checks | CTA heuristic 실패 | 없음 |

## 8. 관찰 내용

### 확인된 것

1. `review` 템플릿에서는 `CTA 강도`도 실제로 유의미한 레버였습니다.
2. 지역 반복은 그대로 유지하면서 CTA만 더 직접적으로 바꾸는 데 성공했습니다.
3. `저장하기`는 `review` 시나리오에 꽤 잘 맞는 행동 표현으로 보입니다.

### 아직 모르는 것

1. `CTA 강도`와 `지역 반복 제약` 중 실제 우선순위가 어느 쪽이 더 높은지는 아직 단일 실행 기준입니다.
2. `저장하기`가 실제 업로드/게시 흐름에서 가장 적합한 CTA인지는 더 봐야 합니다.

## 9. 실패/제약

1. 실험 중 CTA heuristic에 `저장`이 빠져 있어 평가 규칙을 수정해야 했습니다.
2. 단일 실행 1회입니다.

## 10. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `T04 review`에서는 `지역 반복 제약`과 함께 `CTA 강도`도 강한 레버입니다.
  - 특히 마지막 장면의 행동 유도를 짧고 직접적으로 만드는 데 분명한 효과가 있었습니다.

## 11. 다음 액션

1. `T02 promotion`과 `T04 review`의 상위 레버를 비교 표로 정리합니다.
2. 그 다음 `web/capture`가 실제 `scenePlan` artifact를 직접 읽도록 연결합니다.

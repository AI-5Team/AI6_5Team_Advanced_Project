# EXP-15 Service-Aligned B-Grade Tone Guidance

## 1. 기본 정보

- 실험 ID: `EXP-15`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `Gemma 4` prompt lever experiment, `scene-plan` 기준 생성 품질 재개

## 2. 왜 이 실험을 했는가

- `EXP-14`에서 worker 생성 경로가 다시 `scene-plan.json`을 내보내도록 연결했습니다.
- 그 결과 현재 병목이 renderer만이 아니라 deterministic copy planning에도 있다는 점이 분명해졌습니다.
- 따라서 이번에는 hardcoded scene가 아니라 실제 서비스 본선 시나리오 위에서 prompt 실험을 다시 시작했습니다.

## 3. baseline 조건 고정

| 항목 | 고정값 |
|---|---|
| 모델 | `models/gemma-4-31b-it` |
| provider | Google Generative Language API |
| 온도 | `0.2` |
| 업종 | `restaurant` |
| 목적 | `promotion` |
| 스타일 | `b_grade_fun` |
| 지역 | `성수동` |
| 상세 위치 | `서울숲 근처` |
| 템플릿 | `T02` |
| 자산 세트 | `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg` |
| quick options | `highlightPrice=true`, `shorterCopy=true`, `emphasizeRegion=false` |
| 평가 기준 | copy bundle 규칙 점수 + `scene-plan` 길이/중복 지표 |

## 4. 이번에 바꾼 레버

- 바뀐 레버는 **`audience_guidance` 한 가지**입니다.
- baseline prompt:
  - 스타일 기본값만 따르고 추가 톤 지시는 없음
- variant prompt:
  - `B급 감성 = 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤`
  - 추상 표현 금지
  - 혜택/기간감/행동 단어를 앞쪽에 배치

## 5. 실험 중 수정한 기준선 문제

이번 실험을 돌리면서 prompt harness 자체에 두 가지 오염 요인이 있음을 확인했고 먼저 수정했습니다.

1. `T02`가 요구하는 `benefit`, `urgency` 슬롯이 prompt의 JSON shape에 없었습니다.
   - 조치: 템플릿의 실제 `textRole`을 읽어 동적으로 JSON shape를 만들도록 수정했습니다.
2. `예약하기`가 CTA 액션으로 인정되지 않았습니다.
   - 조치: 평가 규칙의 action keyword에 `예약`을 추가했습니다.

즉, 이번 결과는 위 두 문제를 바로잡은 뒤 재실행한 최종 결과입니다.

## 6. 수행 절차

1. `scene-plan` 기반 평가 지표를 prompt harness에 추가했습니다.
2. `EXP-15` 시나리오를 `T02 / b_grade_fun / 실제 음식 사진` 기준으로 고정했습니다.
3. `Gemma 4` baseline prompt와 `B급 톤 guidance` variant를 각각 실행했습니다.
4. artifact를 아래 경로에 저장했습니다.
   - `docs/experiments/artifacts/exp-15-gemma-4-prompt-lever-experiment-service-aligned-b-grade-tone.json`

## 7. 결과 요약

### 정량 요약

| 케이스 | copy score | over-limit scene | repeated copy | 비고 |
|---|---:|---:|---:|---|
| deterministic reference | `92.9` | `3` | `1` | 지역 반복 초과 |
| Gemma baseline prompt | `92.9` | `0` | `0` | 지역 반복 초과 |
| Gemma B급 tone guidance | `100.0` | `0` | `0` | 실패 체크 없음 |

### baseline 대비 차이

| 비교 항목 | Gemma baseline prompt | Gemma B급 tone guidance |
|---|---|---|
| hookText | `육즙 폭발! 성수동 규카츠 미친 할인!` | `성수동 육즙 폭발! 규카츠 미쳤다!` |
| benefit scene | `오늘만 특가 할인!`에 가까운 직접성은 있었지만 전체 톤이 덜 고정됨 | `오늘만 특가 할인!`처럼 혜택이 더 선두에 고정됨 |
| urgency scene | 길이와 직접성은 확보 | `재고 소진 시 종료!`처럼 더 전단지형 문구로 수렴 |
| closing CTA | closing primary가 `예약하기` 계열이 아니어서 scene-plan CTA 강도가 덜 선명 | `지금 바로 예약!`로 마감 장면 CTA가 더 짧고 명확 |
| failed checks | 지역 반복 초과 | 없음 |

## 8. 관찰 내용

### 확인된 것

1. 이제 생성 실험이 hardcoded UI가 아니라 실제 `worker -> template -> scene-plan` 기준으로 다시 돌아오기 시작했습니다.
2. `B급 톤 guidance`는 실제로 의미 있는 레버였습니다.
3. deterministic baseline은 여전히 문구가 길고 둔하며, `b_grade_fun.rules.maxTextPerScene = 16` 기준에서 `s1/s2/s3`가 모두 초과했습니다.
4. Gemma baseline prompt만으로도 길이/중복 측면에서는 deterministic baseline보다 확실히 좋아졌습니다.
5. 그 위에 `B급 톤 guidance`를 추가하면 `failed_checks`가 사라지고 scene별 직접성이 더 강해졌습니다.

### 아직 모르는 것

1. 이번 결과는 단일 실행 1회라 재현성은 아직 부족합니다.
2. `T02`에서는 좋았지만 `T04` review 템플릿에서도 같은 경향이 유지되는지는 아직 모릅니다.
3. scene-plan 기준 개선이 실제 HTML/CSS render surface 품질 체감으로 이어지는지는 아직 별도 확인이 필요합니다.

## 9. 실패/제약

1. 실험 시작 시 prompt harness의 JSON shape가 `T02` 슬롯 구조를 제대로 반영하지 못하고 있었습니다.
2. CTA heuristic이 `예약`을 action으로 보지 않아 1차 결과를 오염시켰습니다.
3. 이번 실험은 `B급 톤 guidance` 한 레버만 봤고, `few-shot`, `CTA 강도`, `지역 강조 방식`은 아직 미실행입니다.

## 10. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `B급 톤 guidance`는 이 프로젝트에서 우선순위가 높은 prompt lever 후보입니다.
  - 특히 `T02 promotion + b_grade_fun` 기준에서는 deterministic baseline보다 짧고 직접적인 scene copy를 만드는 데 분명한 효과가 있었습니다.

## 11. 다음 액션

1. 같은 구조로 `T04 review + b_grade_fun` 실험을 추가합니다.
2. 그 다음 레버는 `CTA 강도`로 고정해 one-variable-at-a-time으로 비교합니다.
3. 이후 web/capture가 hardcoded data 대신 실제 `scenePlan` artifact를 읽도록 연결합니다.

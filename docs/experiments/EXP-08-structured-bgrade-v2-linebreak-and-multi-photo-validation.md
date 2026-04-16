# EXP-08 structured_bgrade_v2 줄바꿈 정리 + 다건 사진 검증

## 1. 기본 정보

- 실험 ID: `EXP-08`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: structured baseline line-break polish, 실제 음식 사진 다건 검증

## 2. 왜 이 실험을 추가했는가

- `EXP-07`에서 baseline rebuild 자체는 성공했지만, headline과 note 줄바꿈이 아직 기계적으로 보였습니다.
- 특히 기존 char-by-char wrapping은 `저장` 같은 단어를 쪼개는 문제가 있었습니다.
- 따라서 baseline을 다음 단계로 넘기기 전에:
  - 단어 경계 기반 줄바꿈으로 정리하고
  - 실제 음식 사진 여러 장에서도 구조가 유지되는지
  함께 확인할 필요가 있었습니다.

## 3. baseline 실험 조건 고정

| 항목 | 고정값 |
|---|---|
| renderer baseline | `structured_bgrade_v2` |
| 스타일 | `b_grade_fun` |
| 템플릿 관점 | `T02` promotion |
| 검증 목적 | line-break 개선 + 다건 사진 안정성 확인 |
| 바뀐 내용 | OVAT 아님, baseline polish |

## 4. 이번에 바꾼 것

1. `wrap_text_by_pixels()`를 단어 우선 줄바꿈으로 수정했습니다.
2. 긴 단어만 필요한 경우에만 문자 단위로 fallback 하도록 바꿨습니다.
3. note 문구를 `사장님 손글씨`로 줄여 side panel 밀도를 낮췄습니다.
4. `EXP-08`을 추가해 아래 실제 음식 사진 5세트로 검증했습니다.
   - `규카츠`
   - `라멘`
   - `순두부짬뽕`
   - `장어덮밥`
   - `타코야키`

## 5. 실험 절차

1. `video_harness.py`의 wrapping 로직을 수정했습니다.
2. `structured_bgrade_v2`를 다시 렌더해 headline/CTA 줄바꿈을 확인했습니다.
3. `EXP-08`을 실행해 실제 음식 사진 5장에 일괄 적용했습니다.
4. 여러 scene 이미지를 직접 확인했습니다.

## 6. 결과

### artifact

- `docs/experiments/artifacts/exp-08-structured-b-grade-v2-multi-photo-validation/summary.json`

### 확인된 것

1. `저장` 같은 단어가 중간에서 찢어지는 문제는 줄었습니다.
2. `규카츠`, `라멘`, `순두부짬뽕`, `장어덮밥`처럼 형태가 다른 음식 사진에서도 구조가 무너지지 않았습니다.
3. side panel, photo zone, footer CTA가 다건 사진에서도 일관되게 유지됐습니다.

### 질적 비교 요약

| 항목 | 개선 전 | 개선 후 |
|---|---|---|
| 한국어 단어 줄바꿈 | 기계적으로 잘림 | 단어 경계 우선 |
| note 가독성 | 과밀 | 완화 |
| 다건 사진 안정성 | 미검증 | 5장 기준 확인 |

## 7. 실패/제약

1. headline이 아주 짧고 강한 B급 카피일 때는 좋지만, 더 긴 문구가 들어오면 추가 조정이 여전히 필요합니다.
2. 다건 사진 검증은 했지만, 아직 자동 overflow 감지는 붙이지 않았습니다.
3. production renderer에는 아직 반영하지 않았습니다.

## 8. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `structured_bgrade_v2`는 단순 시범용이 아니라 실제 baseline 후보로 볼 수 있는 수준까지 올라왔습니다.
  - 다음 단계는 production 반영 전 다건 시나리오를 조금 더 늘리고, quick action 적용 시 시각 차이가 유지되는지 보는 것입니다.

## 9. 다음 액션

1. `structured_bgrade_v2`를 baseline candidate로 유지합니다.
2. 다음은 `quick action visible delta` 검증으로 넘어갑니다.
3. production renderer로 이식할지, experiments 경로에서 한 번 더 다듬을지 판단합니다.

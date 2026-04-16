# EXP-235 Review Template Shot-Aware Policy Check

## 1. 기본 정보

- 실험 ID: `EXP-235`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `T04 review template / shot-aware renderer policy validation`

## 2. 왜 이 작업을 했는가

- `EXP-234`까지로 `T02 / promotion / b_grade_fun` 기준 shot-aware policy는 꽤 안정화됐습니다.
- 하지만 본선에서 같은 스타일을 쓰는 다른 템플릿인 `T04 / review / b_grade_fun`에 그대로 적용해도 무리 없는지는 아직 확인되지 않았습니다.
- 따라서 다음 구현으로 바로 넘어가기 전에 `review` 템플릿에서도 동일 정책이 과하지 않은지 실제 샘플로 확인했습니다.

## 3. 실험 질문

1. `T04 / review / b_grade_fun`에서도 현재 shot-aware policy를 그대로 써도 되는가
2. tray / drink / preserve 세 lane이 `review` 구조에서 부자연스럽게 보이지 않는가

## 4. 실행 조건

### 4.1 샘플군

- `규카츠`
- `맥주`
- `커피`
- `라멘`

### 4.2 공통 조건

- template: `T04`
- purpose: `review`
- style: `b_grade_fun`
- artifact root:
  - `docs/experiments/artifacts/exp-235-review-template-shot-aware-policy-check/`

## 5. 핵심 결과

### 규카츠

- `tray_full_plate`
- scene policy:
  - `s1 cover_center + push_in_center`
  - `s2 cover_center + push_in_center`
  - `s3 cover_center + push_in_center`

### 맥주

- `glass_drink_candidate`
- scene policy:
  - `s1 cover_bottom + push_in_bottom`
  - `s2 cover_bottom + push_in_bottom`
  - `s3 cover_bottom + push_in_bottom`

### 커피

- `glass_drink_candidate`
- scene policy:
  - `s1 cover_top + push_in_top`
  - `s2 cover_top + push_in_top`
  - `s3 cover_top + push_in_top`

### 라멘

- `preserve_shot`
- scene policy:
  - `s1 cover_center + push_in_center`
  - `s2 cover_center + push_in_top`
  - `s3 cover_center + push_in_center`

## 6. 해석

1. `review` 템플릿은 `promotion`과 달리 `period` scene이 없어서, 현재 shot-aware policy가 오히려 더 단순하고 안정적으로 적용됩니다.
2. `규카츠`, `맥주`, `커피`, `라멘` 모두 contact sheet 기준으로 과한 crop이나 blur backdrop 문제가 보이지 않았습니다.
3. 즉 현재 shot-aware renderer policy는 `T02`뿐 아니라 `T04`에서도 그대로 유지 가능하다고 판단하는 편이 맞습니다.

## 7. 결론

- 판정은 `유지`입니다.
- 현재 `b_grade_fun` shot-aware policy는 `promotion`과 `review` 두 템플릿 모두에서 production baseline으로 유지해도 무리가 없습니다.

## 8. 다음 액션

1. renderer baseline 쪽의 즉시 보정 필요사항은 현재 기준으로 크게 줄었습니다.
2. 다음 우선순위는 새 로컬 미세조정보다, 이 baseline을 기준으로 실제 결과 확인 UX나 template/result package 흐름 쪽과 다시 맞물려 보는 것입니다.

## 9. 대표 artifact

- `docs/experiments/artifacts/exp-235-review-template-shot-aware-policy-check/summary.json`
- `docs/experiments/artifacts/exp-235-review-template-shot-aware-policy-check/규카츠/contact_sheet.png`
- `docs/experiments/artifacts/exp-235-review-template-shot-aware-policy-check/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-235-review-template-shot-aware-policy-check/커피/contact_sheet.png`
- `docs/experiments/artifacts/exp-235-review-template-shot-aware-policy-check/라멘/contact_sheet.png`

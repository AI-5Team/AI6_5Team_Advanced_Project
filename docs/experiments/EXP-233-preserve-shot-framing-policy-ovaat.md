# EXP-233 Preserve Shot Framing Policy OVAAT

## 1. 기본 정보

- 실험 ID: `EXP-233`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `preserve_shot framing / contain_blur vs cover_center / b_grade_fun policy refinement`

## 2. 왜 이 작업을 했는가

- `EXP-232`까지 진행한 결과, `drink/tray` lane은 renderer에 잘 옮겨졌지만 `preserve_shot`만 `contain_blur` 배경 존재감이 과하다는 문제가 남았습니다.
- 이 문제는 모델 비교가 아니라 framing policy 하나로 줄어든 상태였기 때문에, 바로 `contain_blur`와 `cover_center`를 비교하는 소규모 OVAAT로 정리하는 편이 맞았습니다.

## 3. 이번 실험 질문

1. `preserve_shot`에서 `contain_blur`가 실제로 필요한가
2. 아니면 단순 `cover_center`가 더 깔끔하고 서비스 친화적인가
3. `period` scene만 별도 top bias를 주는 구조가 유지되어도 전체 템포가 충분한가

## 4. 실험 설계

### 4.1 샘플군

- `라멘`
- `순두부짬뽕`
- `장어덮밥`
- `귤모찌`

### 4.2 비교 variant

1. `contain_blur`
   - preserve scene 기본 framing: `contain_blur`
   - `period` scene만 `cover_top + push_in_top`
2. `cover_center`
   - preserve scene 기본 framing: `cover_center`
   - `period` scene만 `cover_top + push_in_top`

### 4.3 artifact root

- `docs/experiments/artifacts/exp-233-preserve-shot-framing-policy-ovaat/`

## 5. 결과 요약

### 5.1 시각 해석

1. `라멘`
   - `contain_blur`는 오렌지 배경 blur가 너무 크게 깔려 음식 외곽보다 backdrop 존재감이 먼저 들어왔습니다.
   - `cover_center`는 그릇과 국물, 면 디테일이 더 자연스럽고 광고 컷으로도 훨씬 깔끔했습니다.
2. `장어덮밥`
   - `contain_blur`는 tray 외곽 blur가 강해서 화면이 의도적으로 만든 합성처럼 보였습니다.
   - `cover_center`는 메뉴 중심성이 더 직접적이고, `b_grade_fun` 오버레이와도 충돌이 적었습니다.
3. `순두부짬뽕`, `귤모찌`
   - 두 샘플도 공통적으로 `cover_center` 쪽이 cleaner했습니다.
   - 즉 preserve lane에서는 blur backdrop이 품질 이득보다 위화감을 더 크게 만든다고 보는 편이 맞습니다.

### 5.2 결론

- 이번 OVAAT의 판정은 `cover_center 승`입니다.
- `preserve_shot`에서 `contain_blur`를 계속 유지할 근거는 약했고, `cover_center`가 더 서비스 정렬적이었습니다.

## 6. 정책 결정

- `preserve_shot`
  - 기본 scene: `cover_center`
  - detail scene: `cover_center + push_in_top`
  - `period` scene: `cover_top + push_in_top`

## 7. 다음 액션

1. 이 결론을 바로 본선 renderer 정책에 반영합니다.
2. 반영 후 실제 generation sample을 다시 뽑아 rollout check를 진행합니다.

## 8. 대표 artifact

- `docs/experiments/artifacts/exp-233-preserve-shot-framing-policy-ovaat/summary.json`
- `docs/experiments/artifacts/exp-233-preserve-shot-framing-policy-ovaat/contain_blur/라멘/contact_sheet.png`
- `docs/experiments/artifacts/exp-233-preserve-shot-framing-policy-ovaat/cover_center/라멘/contact_sheet.png`
- `docs/experiments/artifacts/exp-233-preserve-shot-framing-policy-ovaat/contain_blur/장어덮밥/contact_sheet.png`
- `docs/experiments/artifacts/exp-233-preserve-shot-framing-policy-ovaat/cover_center/장어덮밥/contact_sheet.png`

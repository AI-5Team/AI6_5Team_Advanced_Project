# EXP-62 Cross-project variant publish guard

## 1. 기본 정보

- 실험 ID: `EXP-62`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `서비스 본선 publish variant 프로젝트 경계 검증`

## 2. 왜 이 작업을 했는가

- `EXP-60`에서 stale variant는 같은 프로젝트 안에서 막힌다는 점을 확인했습니다.
- 다음으로 확인해야 하는 것은 다른 프로젝트의 `variantId`를 넣었을 때도 publish가 안전하게 거부되는지입니다.

## 3. baseline

### 고정한 조건

1. 경로: `runtime API test + web demo route`
2. 프로젝트 개수: `2`
3. 업종/목적/스타일: 둘 다 `restaurant / promotion / b_grade_fun`
4. 템플릿: 둘 다 `T02`
5. 자산: 둘 다 `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg`
6. 게시 채널/모드: `youtube_shorts / assist`

### 이번에 바꾼 레버

- `variantId` 소속만 바꿨습니다.
- baseline: 현재 프로젝트 자신의 latest variant
- variant: 다른 프로젝트의 latest variant

## 4. 무엇을 바꿨는가

1. API 테스트 `services/api/tests/test_api_smoke.py`에 cross-project variant 거부 시나리오를 추가했습니다.
2. 검증 스크립트 `scripts/check_cross_project_variant_publish_guard.mjs`를 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-62-cross-project-variant-publish-guard/summary.json`

### baseline 대비 차이

- project A variant를 project B publish에 넣으면:
  - status: `422`
  - error code: `INVALID_STATE_TRANSITION`
- project B 자신의 variant를 넣으면:
  - status: `assist_required`
  - assist package 정상 생성

### 확인된 것

1. publish는 이제 project boundary를 넘는 `variantId`를 받지 않습니다.
2. `variantId`는 단순 존재 여부가 아니라 현재 프로젝트 latest selected result와 연결돼야 합니다.
3. 본선 쪽 publish guard는 stale/cross-project 둘 다 커버하게 됐습니다.

## 6. 실패/제약

1. 이번 검증은 `assist` 경로 기준입니다.
2. schedule 경로는 아직 같은 검증을 붙이지 않았습니다.
3. 외부 SNS provider 실제 호출까지 본 것은 아닙니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - publish contract는 stale variant뿐 아니라 cross-project variant 혼입도 막는 수준까지 올라왔습니다.

## 8. 다음 액션

1. schedule 경로가 생기면 같은 variant guard를 그대로 재사용해야 합니다.
2. 본선은 이제 variant guard보다 생성 품질 쪽에 다시 비중을 줄 수 있습니다.

# 테스트 시나리오 65 - cross-project variant publish guard

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-65`

## 2. 테스트 목적

- 다른 프로젝트의 `variantId`를 넣은 publish 요청이 안전하게 거부되는지 확인합니다.

## 3. 수행 항목

1. `uv run --project services/api pytest services/api/tests/test_api_smoke.py -k cross_project_variant`
2. `node scripts/check_cross_project_variant_publish_guard.mjs`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-62-cross-project-variant-publish-guard/summary.json`

## 5. 관찰 내용

1. project A의 variant를 project B publish에 넣으면 `422 INVALID_STATE_TRANSITION`이 반환됐습니다.
2. project B 자신의 variant를 쓰면 `assist_required`가 정상 반환됐습니다.
3. cross-project variant 혼입은 현재 demo/runtime 기준으로 모두 차단됩니다.

## 6. 실패/제약

1. `assist` 경로만 확인했습니다.
2. schedule 경로는 아직 별도 확인하지 않았습니다.

## 7. 개선 포인트

1. schedule 구현 시에도 같은 project/variant guard를 재사용해야 합니다.
2. history나 result 화면에서 stale publish retry가 생기지 않도록 UX도 계속 맞춰야 합니다.

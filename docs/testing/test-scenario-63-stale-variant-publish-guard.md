# 테스트 시나리오 63 - stale variant publish guard

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-63`

## 2. 테스트 목적

- regenerate 이후 오래된 `variantId`로 publish를 시도했을 때 API가 이를 거부하는지 확인합니다.

## 3. 수행 항목

1. `uv run --project services/api pytest services/api/tests/test_api_smoke.py -k stale_variant`
2. `node scripts/check_stale_variant_publish_guard.mjs`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-60-stale-variant-publish-guard/summary.json`

## 5. 관찰 내용

1. regenerate 후 baseline variant와 regenerated variant가 실제로 달라졌습니다.
2. baseline variant로 publish를 시도하면 `422 INVALID_STATE_TRANSITION`이 반환됐습니다.
3. regenerated variant로 다시 publish하면 `assist_required`가 정상 반환됐습니다.
4. 이 검증 과정에서 regenerate derivative unique 충돌도 재현됐고, upsert 수정 후 해결됐습니다.

## 6. 실패/제약

1. `assist` 경로 중심 검증입니다.
2. cross-project variant 혼입은 아직 별도 테스트하지 않았습니다.

## 7. 개선 포인트

1. runtime과 demo route 모두 stale variant 규칙을 계속 같은 수준으로 유지해야 합니다.
2. 필요하면 schedule 경로도 같은 guard를 붙여 확인합니다.

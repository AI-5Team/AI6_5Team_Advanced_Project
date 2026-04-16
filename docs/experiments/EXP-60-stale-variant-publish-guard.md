# EXP-60 Stale variant publish guard

## 1. 기본 정보

- 실험 ID: `EXP-60`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `서비스 본선 publish variant 검증 / regenerate 안정성`

## 2. 왜 이 작업을 했는가

- `EXP-59`에서 latest result와 assist package의 일관성은 확인됐습니다.
- 하지만 그 검증은 항상 최신 `variantId`를 넘긴 경우였고, 오래된 `variantId`를 넣었을 때 안전한지는 아직 비어 있었습니다.
- API 계약 문서에는 `variantId`가 현재 프로젝트의 선택 가능한 결과물이어야 한다고 적혀 있습니다.

## 3. baseline

### 고정한 조건

1. 경로: `runtime API test + web demo route`
2. 업종/목적/스타일: `restaurant / promotion / b_grade_fun`
3. 템플릿: `T02`
4. 자산: `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg`
5. 게시 채널/모드: `youtube_shorts / assist`

### baseline 문제

1. `services/api/app/services/runtime.py`는 `variantId` 존재 여부만 전역으로 확인하고 있었습니다.
2. `apps/web/src/lib/demo-store.ts`는 요청된 `variantId`와 무관하게 최신 run 결과로 assist package를 만들고 있었습니다.
3. `apps/web/src/app/api/projects/[projectId]/publish/route.ts`는 모든 예외를 `404 PROJECT_NOT_FOUND`로 뭉뚱그리고 있었습니다.
4. stale variant 검증 중 regenerate가 `asset_derivatives(asset_id, derivative_type)` unique 제약으로 터지는 문제도 같이 드러났습니다.

## 4. 무엇을 바꿨는가

1. `apps/web/src/lib/demo-store.ts`
   - publish 시 `request.variantId === current result.variantId`가 아니면 `INVALID_STATE_TRANSITION`을 던지도록 바꿨습니다.
2. `apps/web/src/app/api/projects/[projectId]/publish/route.ts`
   - `INVALID_STATE_TRANSITION`을 `422`로, `INVALID_INPUT`을 `400`으로 매핑하도록 바꿨습니다.
3. `services/api/app/services/runtime.py`
   - `variantId`가 최신 generation run의 selected variant인지 검증하도록 강화했습니다.
4. `services/worker/pipelines/generation.py`
   - regenerate 시 같은 derivative를 다시 만들면 upsert 하도록 바꿨습니다.
5. 검증 스크립트
   - `scripts/check_stale_variant_publish_guard.mjs`

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-60-stale-variant-publish-guard/summary.json`

### baseline 대비 차이

- regenerate 후 variant가 실제로 바뀌었습니다.
  - baseline variant: `751136c2-...`
  - regenerated variant: `76883ab9-...`
- stale publish 요청:
  - status: `422`
  - error code: `INVALID_STATE_TRANSITION`
- fresh publish 요청:
  - status: `assist_required`
  - fresh variant 기준 assist package 정상 생성

### 확인된 것

1. 오래된 `variantId`는 이제 demo/runtime 모두에서 거부됩니다.
2. regenerate 이후 publish는 최신 variant로만 이어집니다.
3. stale variant 검증 중 드러난 regenerate derivative unique 충돌도 함께 제거됐습니다.

## 6. 실패/제약

1. 이번 검증은 `assist` 경로 기준입니다.
2. cross-project variant 오염은 별도 시나리오로 아직 보지 않았습니다.
3. 외부 SNS provider 실제 호출까지 검증한 것은 아닙니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - publish는 이제 계약 문서에 맞게 `현재 선택 가능한 결과물`만 받습니다.
  - 이번 턴에서 본선 쪽 위험 하나를 명확히 줄였습니다.

## 8. 다음 액션

1. 필요하면 cross-project variant 요청도 별도 시나리오로 확인합니다.
2. 본선은 stale variant보다 생성 품질 쪽으로 다시 비중을 옮겨도 됩니다.

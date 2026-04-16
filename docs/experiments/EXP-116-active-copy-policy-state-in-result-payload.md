# EXP-116 Active Copy Policy State In Result Payload

## 목적

- `locationPolicy`가 template-spec에만 보이는 static rule이 아니라, 실제 결과 payload 기준 active state로도 드러나는지 확인합니다.
- 결과/이력 화면이 `templateId`만 다시 계산한 추정값이 아니라, worker packaging 시점의 `copyPolicy`를 그대로 읽도록 기준선을 맞춥니다.

## 변경 범위

- `services/worker/pipelines/generation.py`
  - `render-meta.json`에 `copyPolicy`를 추가했습니다.
  - 포함 필드:
    - `detailLocationPolicyId`
    - `forbiddenDetailLocationSurfaces`
    - `guardActive`
    - `emphasizeRegionRequested`
    - `detailLocationPresent`
- `services/api/app/services/runtime.py`
  - `/api/projects/{projectId}/result` 응답에 `copyPolicy`를 그대로 포함합니다.
- `apps/web/src/lib/demo-store.ts`
  - demo-store fallback result도 같은 `copyPolicy` shape를 생성합니다.
- `apps/web/src/components/copy-policy-summary.tsx`
  - static `copy-rule`만 보여주던 카드가, active payload가 있으면 `guard active / inactive` 상태와 `emphasizeRegionRequested`를 함께 보여주도록 확장했습니다.
- `apps/web/src/components/demo-workbench.tsx`
- `apps/web/src/components/history-board.tsx`
  - 결과/이력 카드가 `result.copyPolicy`를 `CopyPolicySummary`에 직접 전달합니다.

## 결과

- 이제 `locationPolicy`는 세 층에서 같은 기준으로 보입니다.
  - template-spec static rule
  - worker packaging 시점 active state
  - web result/history preview state
- 따라서 이후 `policyId` 전환이나 exception rule을 넣더라도, 화면에서 지금 어떤 상태가 적용 중인지 즉시 확인할 수 있습니다.

## 판단

- `emphasizeRegion`은 여전히 `regionName` 강조 요청일 뿐이고, `detailLocation` guard 해제 신호는 아닙니다.
- 이 판단은 이제 evaluator 문서뿐 아니라 result payload에도 남기게 됐습니다.

## 남은 과제

- `scenePlan` preview 카드에도 `active copy policy`를 같이 노출할지 판단이 남아 있습니다.
- 장기적으로는 `copyPolicy`를 `render-meta` 보조 정보가 아니라, 계약된 result schema의 canonical payload로 더 엄격히 다루는 정리가 필요합니다.

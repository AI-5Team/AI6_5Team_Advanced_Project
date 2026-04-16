# Test Scenario 119 - Scene Plan Preview Active Policy Visibility

## 목적

- `scenePlan` preview 카드가 `result.copyPolicy`를 받아 active policy state를 같이 보여주는지 확인합니다.

## 확인 항목

1. `ScenePlanPreviewLinks`
   - `activePolicy` prop을 받을 수 있어야 합니다.
   - `detailLocationPolicyId`, `guard 활성/비활성` 상태가 렌더됩니다.
2. `demo-workbench`
   - `activeResult.copyPolicy`를 scene preview 카드에 전달합니다.
3. `history-board`
   - `result.copyPolicy`를 scene preview 카드에 전달합니다.
4. web build
   - 타입 오류 없이 `next build`가 통과합니다.

## 실행

```powershell
npm run build:web
```

## 기대 결과

- 결과/이력 화면에서 scene preview 링크 위에 현재 `strict_all_surfaces`와 `guard 활성` 상태를 함께 볼 수 있습니다.

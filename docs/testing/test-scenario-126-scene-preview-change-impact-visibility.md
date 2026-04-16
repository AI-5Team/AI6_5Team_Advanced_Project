# Test Scenario 126 - Scene Preview Change Impact Visibility

## 목적

- scene preview 카드가 `changeImpactSummary`를 타입 오류 없이 읽고, opening/closing scene 진입 전에 변경 영향을 보여주는지 확인합니다.

## 확인 항목

1. scene preview card
   - `changeImpactSummary.runType`가 `초기 생성` 또는 `재생성`으로 보입니다.
   - `impactLayers`가 chip으로 표시됩니다.
   - active action이 있으면 label chip이 같이 보입니다.
2. main/history wiring
   - `demo-workbench`, `history-board`가 모두 `result.changeImpactSummary`를 `ScenePlanPreviewLinks`로 전달합니다.
3. web build
   - scene preview 카드 확장 후에도 빌드가 깨지지 않습니다.

## 실행

```powershell
npm run build:web
```

## 기대 결과

- scene preview 카드에서 scene-layer map과 copy policy뿐 아니라 최근 변경 영향까지 같이 읽을 수 있습니다.

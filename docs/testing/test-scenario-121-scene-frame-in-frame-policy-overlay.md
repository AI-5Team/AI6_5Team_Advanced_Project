# Test Scenario 121 - Scene Frame In-Frame Policy Overlay

## 목적

- `scene-frame` project route에서 frame 위 compact policy overlay가 노출되는지 확인합니다.
- `clean=1` query로 overlay를 숨길 수 있는지 확인합니다.

## 확인 항목

1. 기본 project route
   - in-frame overlay가 보입니다.
   - `detailLocationPolicyId`, `guard 활성/비활성`, 금지 surface 요약이 표시됩니다.
2. `clean=1` route
   - 상단 설명 배너는 유지되지만 in-frame overlay는 숨겨집니다.
3. artifact route
   - 기존처럼 overlay 없이 동작합니다.
4. web build
   - `next build`가 통과합니다.

## 실행

```powershell
npm run build:web
```

## 기대 결과

- `/scene-frame/s1?projectId=...`에서는 overlay가 보이고, `/scene-frame/s1?projectId=...&clean=1`에서는 overlay가 숨겨집니다.

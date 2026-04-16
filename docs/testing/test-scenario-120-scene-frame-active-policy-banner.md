# Test Scenario 120 - Scene Frame Active Policy Banner

## 목적

- project 기반 `scene-frame` 페이지가 `copyPolicy` active state를 함께 보여주는지 확인합니다.

## 확인 항목

1. `loadProjectScenePlan()`
   - `/result`에서 `copyPolicy`를 같이 읽어 반환합니다.
2. `scene-frame/[scene]/page.tsx`
   - project route일 때 상단 배너가 렌더됩니다.
   - `detailLocationPolicyId`, `guard 활성/비활성`, 금지 surface 요약이 표시됩니다.
3. artifact route
   - 기존처럼 policy 배너 없이 frame 확인 경로가 유지됩니다.
4. web build
   - 타입 오류 없이 `next build`가 통과합니다.

## 실행

```powershell
npm run build:web
```

## 기대 결과

- `/scene-frame/s1?projectId=...` 기준으로 opening frame 위에 active copy policy 배너가 같이 보입니다.

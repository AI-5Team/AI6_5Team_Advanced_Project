# EXP-118 Scene Frame Active Policy Banner

## 목적

- `scenePlan` preview 카드뿐 아니라 실제 `scene-frame` 화면 안에서도 현재 결과의 `copyPolicy` active state를 다시 확인할 수 있게 합니다.
- 사용자가 opening/closing frame을 볼 때, 그 frame이 어떤 상세 위치 정책 상태를 전제로 생성됐는지 바로 읽을 수 있게 합니다.

## 변경 범위

- `apps/web/src/lib/scene-plan.ts`
  - `loadProjectScenePlan()`이 이제 `/result`에서 `copyPolicy`도 함께 읽어 반환합니다.
- `apps/web/src/app/scene-frame/[scene]/page.tsx`
  - project 기반 scene-frame일 때 상단 배너를 추가했습니다.
  - 배너에는 다음이 표시됩니다.
    - `detailLocationPolicyId`
    - `guard 활성 / 비활성`
    - 금지 surface 요약
    - `emphasizeRegionRequested`가 있어도 guard 유지됨을 다시 확인하는 문장

## 결과

- 이제 사용자는 결과 카드 -> scene preview 카드 -> scene-frame 실제 화면까지 같은 `copyPolicy` active state를 연속해서 확인할 수 있습니다.
- artifact 기반 scene-frame은 기존처럼 순수 frame 확인 용도로 유지하고, project 기반 scene-frame에만 배너를 노출합니다.

## 판단

- `scene-frame`에서도 정책 상태가 보여야 사용자가 “이 컷이 어떤 공개 정책을 전제로 만들어졌는지”를 흐름 안에서 잃지 않습니다.
- 다만 full-frame 캡처만 필요한 경우를 고려해, 현재는 project route에만 얇은 상단 배너를 두는 수준으로 제한했습니다.

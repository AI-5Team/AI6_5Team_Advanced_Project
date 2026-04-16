# EXP-119 Scene Frame In-Frame Policy Overlay

## 목적

- `scene-frame` 상단 배너만으로는 프레임 검토 중 맥락이 끊기는 문제가 있어, 실제 frame 위에서도 핵심 `copyPolicy` 상태를 바로 읽을 수 있게 합니다.
- 다만 frame 자체를 깨끗하게 봐야 하는 경우도 있어 `clean mode`로 overlay를 숨길 수 있게 합니다.

## 변경 범위

- `apps/web/src/app/scene-frame/[scene]/page.tsx`
  - project 기반 route에서 frame wrapper 안쪽 좌측 상단에 compact policy overlay를 추가했습니다.
  - 표시 항목:
    - `detailLocationPolicyId`
    - `guard 활성 / 비활성`
    - `지역명 강조 요청`
    - 금지 surface 요약
  - `?clean=1` query가 있으면 in-frame overlay를 숨깁니다.
  - 상단 설명 배너에는 현재 overlay 표시 여부와 `clean mode` 사용법을 같이 적었습니다.

## 결과

- 사용자는 frame 자체를 보면서도 현재 컷이 어떤 location policy 상태를 전제로 열렸는지 즉시 읽을 수 있습니다.
- 동시에 `clean=1`로 overlay를 숨겨 깔끔한 frame 확인 경로도 유지됩니다.

## 판단

- `scene-frame`에서는 verbose policy 설명보다 compact overlay가 더 자연스럽습니다.
- 현재는 project route에만 overlay를 붙였고, artifact route는 기존처럼 분석 기준선 화면으로 유지합니다.

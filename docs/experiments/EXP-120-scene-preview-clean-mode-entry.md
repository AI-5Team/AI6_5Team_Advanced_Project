# EXP-120 Scene Preview Clean Mode Entry

## 목적

- `scene-frame`에 `clean=1` 모드가 생겼지만, 사용자가 preview 카드에서 바로 그 경로를 선택할 수 있어야 합니다.
- 일반 검토 모드와 clean frame 확인 모드를 링크 단계에서 분리합니다.

## 변경 범위

- `apps/web/src/components/scene-plan-preview-links.tsx`
  - opening / closing scene 각각에 대해 링크를 두 개씩 제공합니다.
    - `일반 보기`
    - `clean mode`
  - 따라서 사용자는 preview 카드에서 바로 overlay 포함 검토 모드와 clean mode를 선택할 수 있습니다.

## 결과

- `scene preview -> scene-frame` 진입 동선에서 mode 선택이 명시적으로 드러납니다.
- clean mode가 URL 파라미터 지식에 의존하지 않게 됐습니다.

## 판단

- `clean=1`은 유용하지만 숨겨진 기능으로 두면 활용도가 떨어집니다.
- preview 카드에서 명시적 버튼으로 노출하는 편이 운영/검토 흐름에 더 맞습니다.

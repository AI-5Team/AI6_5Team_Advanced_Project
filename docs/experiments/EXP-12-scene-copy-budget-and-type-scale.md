# EXP-12 Scene Copy Budget and Type Scale

## 1. 기본 정보

- 실험 ID: `EXP-12`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: scene copy budget, typography scale, HTML/CSS scene polish

## 2. 왜 이 실험을 추가했는가

- `EXP-11`까지 오면서 render surface는 `HTML/CSS + browser capture`가 맞다는 점은 확인했습니다.
- 하지만 `closing` scene처럼 문구 길이가 조금만 길어져도 타이포가 무너지거나, 반대로 너무 작아지는 문제가 남아 있었습니다.
- 따라서 이번에는 문구를 감으로 쓰지 않고, `scene type별 copy budget`과 `type scale`을 코드로 고정하는 실험을 진행했습니다.

## 3. baseline

- 기준선: `EXP-11`
- 문제:
  - 장면별 line budget이 없어서 문구가 layout을 밀어냈음
  - `closing` scene에서 headline/body/kicker가 서로 경쟁했음
  - `review`형 장면 규칙이 없어서 서비스 목적별 장면 확장이 어려웠음

## 4. 이번 실험에서 바꾼 것

1. `opening / review / closing` 3종 scene type을 명시했습니다.
2. 각 scene type마다 아래 규칙을 추가했습니다.
   - headline line 수
   - headline 한 줄 최대 문자 수
   - body/kicker/cta 최대 줄 수
   - type scale
3. `applyTextBudget()` 유틸을 추가해 줄 수와 문자 수를 초과하면 자동으로 줄이고 잘라내도록 했습니다.
4. `review` scene를 새로 추가했습니다.
5. `capture_scene_lab_frames.mjs`도 `review` frame까지 함께 캡처하도록 확장했습니다.
6. 포트 충돌로 예전 build를 잘못 캡처하던 문제를 막기 위해, 캡처 스크립트가 매 실행 시 빈 포트를 찾아 쓰도록 수정했습니다.

## 5. 결과

### 확인된 것

1. 이제 장면이 `문구 때문에 깨지는 것`은 크게 줄었습니다.
2. `closing` scene는 이전처럼 겹치거나 뭉개지지 않고, 최소한 headline/cta가 안정적으로 남습니다.
3. `review` scene도 추가되면서 서비스 목적별 3종 장면 실험이 가능해졌습니다.

### artifact

- `docs/experiments/artifacts/exp-11-html-css-scene-capture/scene-opening.png`
- `docs/experiments/artifacts/exp-11-html-css-scene-capture/scene-review.png`
- `docs/experiments/artifacts/exp-11-html-css-scene-capture/scene-closing.png`

## 6. 실패/제약

1. 무너짐은 줄었지만, subcopy가 너무 말라 보이는 trade-off가 생겼습니다.
2. 특히 `closing` scene의 body/kicker는 안전해진 대신 존재감이 너무 약합니다.
3. 즉 지금은 `layout integrity`는 좋아졌지만 `copy richness`는 일부 희생된 상태입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 현재 단계에서는 먼저 `copy budget`을 강하게 거는 편이 맞습니다.
  - 다만 다음 단계는 문구를 다시 늘리는 것이 아니라, `하단 panel 비율`과 `subcopy typography hierarchy`를 손보는 쪽이어야 합니다.

## 8. 다음 액션

1. `closing` scene의 bottom panel height를 늘리고 subcopy hierarchy를 다시 잡습니다.
2. `review` scene의 정보량을 조금 더 살리되 budget은 유지합니다.
3. 그 다음 worker render path 이식 여부를 판단합니다.

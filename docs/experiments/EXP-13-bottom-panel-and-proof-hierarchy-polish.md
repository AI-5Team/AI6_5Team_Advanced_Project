# EXP-13 Bottom Panel and Proof Hierarchy Polish

## 1. 기본 정보

- 실험 ID: `EXP-13`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: closing bottom panel polish, review proof hierarchy polish

## 2. 왜 이 실험을 추가했는가

- `EXP-12`로 scene copy budget은 고정됐지만, 그 결과 `closing` subcopy가 지나치게 마르고 `review` proof가 약하게 보이는 문제가 남았습니다.
- 따라서 이번에는 문구 길이 규칙은 유지한 채, `패널 비율`과 `subcopy hierarchy`만 다시 다듬었습니다.

## 3. baseline

- 기준선: `EXP-12`
- 문제:
  - `closing`은 headline/cta는 안정적이지만 중간 설명층이 약했음
  - `review`는 body가 proof처럼 보이기보다 작은 문단처럼 보였음

## 4. 이번 실험에서 바꾼 것

1. `closing`
   - bottom panel 높이를 늘렸습니다.
   - 상단 visual 영역에서는 headline만 남기고, body는 하단 panel로 내렸습니다.
   - body를 stronger subcopy로 올리고, kicker는 muted line으로 다시 분리했습니다.
2. `review`
   - body를 일반 문단 대신 `quote/proof block`처럼 보이게 바꿨습니다.
   - CTA 크기를 조금 낮추고, proof 텍스트의 존재감을 올렸습니다.

## 5. 결과

### 확인된 것

1. `closing` scene는 이전보다 “왜 지금 업로드해야 하는가”가 더 읽힙니다.
2. `review` scene는 단순 설명보다 실제 반응을 보여주는 장면처럼 보이기 시작했습니다.
3. copy budget을 유지한 상태에서도 hierarchy만으로 설득력을 일부 복구할 수 있다는 점을 확인했습니다.

### artifact

- `docs/experiments/artifacts/exp-11-html-css-scene-capture/scene-review.png`
- `docs/experiments/artifacts/exp-11-html-css-scene-capture/scene-closing.png`

## 6. 실패/제약

1. `closing`은 아직도 풍부한 정보량보다는 안전성 쪽에 더 치우쳐 있습니다.
2. `review`는 좋아졌지만, 실제 사용자 평가 없이는 proof 강도를 단정하기 어렵습니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 다음 단계는 문구를 늘리는 것이 아니라, 현재 hierarchy를 유지한 채 motion이나 worker 이식 가능성을 보는 편이 맞습니다.

## 8. 다음 액션

1. current HTML/CSS scene를 worker render path로 옮길 수 있는지 구조를 확인합니다.
2. 혹은 그 전에 동일 scene를 5개 이상 메뉴 사진으로 다시 검증합니다.

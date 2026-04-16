# EXP-107 Gemma 4 benefit 14 char cap

## 1. 기본 정보

- 실험 ID: `EXP-107`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `Gemma 4 / benefit headline cap / render-ready headroom`

## 2. 왜 이 작업을 했는가

- `EXP-105`에서 `Gemma 4`는 region anchor는 잘 지켰지만, benefit headline이 한 글자 길어지면서 `s2`가 over-limit였던 run이 있었습니다.
- 이번에는 strict region anchor baseline은 유지하고, `benefit primaryText를 12~14자 안쪽`으로 더 직접적으로 묶었습니다.

## 3. 비교축

1. baseline
   - `fixed_reference_hook_region_anchor_budget_gemma`
2. candidate
   - `reference_hook_benefit_14_cap_gemma`

## 4. 실행 결과

artifact:

- `docs/experiments/artifacts/exp-107-gemma-4-prompt-lever-experiment-benefit-14-char-cap.json`

### baseline

- score: `100.0`
- hook:
  - `오늘 안 오면 진짜 손해인가요?`
- benefit:
  - `육즙 팡팡 규카츠+맥주 할인!`
- cta:
  - `예약하고 방문하기`
- headline lengths:
  - `s1=14`, `s2=16`, `s3=13`, `s4=11`

### candidate

- score: `100.0`
- hook:
  - `오늘 안 오면 진짜 손해인가요?`
- benefit:
  - `규카츠+맥주 파격 할인`
- cta:
  - `방문해서 혜택 받기`
- headline lengths:
  - `s1=14`, `s2=12`, `s3=12`, `s4=10`

## 5. 해석

- benefit 14자 cap 자체는 실제로 먹혔습니다.
  - benefit headline이 `16 -> 12`로 줄었습니다.
  - 전체 headline 길이도 좀 더 여유가 생겼습니다.
- 다만 baseline도 이번 run에서는 이미 `score 100`이었기 때문에, `점수 역전`이나 `실패 복구` 수준의 변화는 아니었습니다.
- candidate는 대신 `#서울숲데이트` 같은 nearby landmark 계열 hashtag를 다시 섞었습니다.

## 6. 결론

- `Gemma 4`는 현재 strict anchor 계열 prompt에서 이미 꽤 안정적입니다.
- benefit 14자 cap은 `유효한 미세 tuning`이지만, 본선을 바꿀 정도의 승부수는 아닙니다.
- 오히려 현재 남은 리스크는 `길이`보다 `근처/데이트/서울숲` 같은 부가 위치 표현이 다시 섞이는 점입니다.

## 7. 다음 액션

1. `Gemma 4`는 benefit 14자 cap을 유지 후보로 남깁니다.
2. 대신 location leakage는 별도 평가 축으로 다뤄야 합니다.
3. 최종 판단은 `EXP-108` 비교와 `EXP-109` repeatability까지 보고 내립니다.

## 8. 평가기 보강 후 메모

- `EXP-110` 패치 후 baseline은 `93.3`, candidate는 `100.0`이었습니다.
- baseline은 nearby-location leakage가 새 평가기에서 잡혔고, candidate는 이번 run 기준으로 leakage 없이 통과했습니다.
- 따라서 이 실험은 지금 기준에서 `Gemma 4` 쪽 실효 tuning으로 유지할 가치가 있습니다.

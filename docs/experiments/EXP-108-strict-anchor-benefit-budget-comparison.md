# EXP-108 Strict anchor benefit budget comparison

## 1. 기본 정보

- 실험 ID: `EXP-108`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `Gemma 4 vs gpt-5-mini / exact region anchor / tighter benefit budget`

## 2. 왜 이 작업을 했는가

- `EXP-106`과 `EXP-107`을 보면 두 모델 모두 각자 맞는 tuning 방향은 보였습니다.
- 하지만 실제 선택은 `각자 다른 prompt에서 잘 나온다`가 아니라, `지금 가장 production-near한 strict prompt에서 누가 더 안정적인가`로 봐야 합니다.
- 그래서 이번에는 `exact region anchor + benefit 14자 cap`을 함께 묶은 동일 prompt로 `Gemma 4`와 `gpt-5-mini`를 다시 붙였습니다.

## 3. 고정 조건

1. `hook`
   - 14자 안팎
2. `benefit`
   - 12~14자, 14자 초과 금지
3. `urgency / cta`
   - 각각 10자 / 8자 안팎
4. `region`
   - primary headline에는 금지
   - caption 1개에는 `성수동` exact string 1회
   - hashtag 1개에는 `성수동` exact string 1회
   - nearby landmark 우회 표현 금지

## 4. 실행 결과

artifact:

- `docs/experiments/artifacts/exp-108-reference-hook-strict-anchor-benefit-budget-comparison.json`

### Gemma 4

- score: `100.0`
- hook:
  - `미친 규카츠 할인, 오늘만?`
- cta:
  - `예약하고 방문하기`
- failed:
  - 없음
- headline lengths:
  - `s1=15`, `s2=12`, `s3=10`, `s4=8`

관찰:

- 자동 평가 기준에서는 완전히 통과했습니다.
- `성수동` caption + hashtag도 모두 채웠습니다.
- CTA는 여전히 `gpt-5-mini`보다 길지만, 현재 평가 기준에서는 크게 흔들리지 않았습니다.

### GPT-5 Mini

- score: `92.9`
- hook:
  - `오늘만 규카츠 할인?`
- cta:
  - `방문`
- failed:
  - `region appears in fewer than required areas`
- headline lengths:
  - `s1=11`, `s2=16`, `s3=10`, `s4=10`

관찰:

- 길이와 CTA 직접성은 더 좋았습니다.
- 하지만 caption에서 `성수동`을 빼고 `서울숲 근처`로 우회했습니다.
- hashtag에 `#성수동`은 있었지만, exact region slot 2개 조건을 못 채웠습니다.

## 5. 해석

- 같은 strict prompt에서 보면 현재는 `Gemma 4`가 더 production-near합니다.
- `gpt-5-mini`는 톤과 길이는 더 공격적이고 좋지만, region anchor 쪽이 계속 흔들립니다.
- 즉 지금 기준의 분기점은 다시 확인됐습니다.
  - `Gemma 4`: exact region anchor와 구조 안정성 강점
  - `gpt-5-mini`: 짧고 직설적인 광고 톤 강점

## 6. 결론

- strict prompt 기준 현재 1순위 후보는 `Gemma 4`입니다.
- `gpt-5-mini`는 메인 baseline보다는 `tone reference` 또는 `짧은 카피 아이디어 후보`에 더 가깝습니다.

## 7. 다음 액션

1. `EXP-109` repeatability로 이 판단이 재현되는지 확인합니다.
2. 자동 평가기가 nearby landmark leakage를 놓치는 문제를 문서에 명시합니다.
3. 본선 모델 baseline 판단은 `Gemma 4 우선`, `gpt-5-mini 보조`로 정리합니다.

## 8. 평가기 보강 후 메모

- `EXP-110` 패치 후 최신 결과는 `Gemma 4 = 100.0`, `gpt-5-mini = 93.3`입니다.
- `gpt-5-mini`의 핵심 실패는 이제 `region slot miss`보다 `nearby location leaked into strict region budget`로 더 명확하게 드러납니다.
- 최신 평가 기준에서도 strict prompt의 1순위 후보는 `Gemma 4`입니다.

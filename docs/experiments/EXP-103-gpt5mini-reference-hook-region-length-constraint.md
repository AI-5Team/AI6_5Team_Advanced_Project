# EXP-103 GPT-5 Mini reference hook region/length constraint

## 1. 기본 정보

- 실험 ID: `EXP-103`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `gpt-5-mini constraint tuning / region budget / length cap`

## 2. 왜 이 작업을 했는가

- `EXP-102`에서 `gpt-5-mini`는 CTA와 hook는 짧고 직접적이었지만, run-to-run variation과 region repeat/scene length 흔들림이 남았습니다.
- 이번 실험은 `reference hook guidance` 위에 `region/length constraint`를 더 직접적으로 얹어서, 그 흔들림을 줄일 수 있는지 확인하는 OVAT입니다.

## 3. 비교축

1. baseline
   - `fixed_reference_hook_pack_guidance_openai`
2. candidate
   - `reference_hook_pack_region_length_constraint_openai`

## 4. 추가한 constraint

1. `hookText / hook primary`
   - 14자 안팎
2. `benefit / urgency / cta primary`
   - 각각 16자 / 10자 / 8자 안팎
3. `benefit, urgency, cta primary`
   - 지역명 금지
4. `captions`
   - 지역명은 최대 1개 caption에서 1회만 허용
5. `hashtags`
   - 지역명이 들어간 hashtag는 최대 1개
6. `cta`
   - 방문/저장/확인/예약으로 시작

## 5. 실행 결과

artifact:

- `docs/experiments/artifacts/exp-103-gpt-5-mini-prompt-lever-experiment-reference-hook-region-length-constraint.json`

### baseline

- score: `100.0`
- hook:
  - `오늘만 규카츠+맥주 할인!`
- cta:
  - `지금 방문`
- over-limit:
  - `s2`, `s3`

### candidate

- score: `92.9`
- hook:
  - `오늘만 규카츠 반값?!`
- cta:
  - `방문`
- over-limit:
  - 없음
- failed:
  - `region appears in fewer than required areas`

## 6. 해석

- 길이 constraint 자체는 분명히 효과가 있었습니다.
  - over-limit scene이 `2개 -> 0개`로 줄었습니다.
  - hook/cta도 더 짧아졌습니다.
- 하지만 region budget을 너무 강하게 묶으면서, 이번 run에서는 지역 반영 최소조건을 놓쳤습니다.
- 특히 모델이 `성수동` 대신 `서울숲 근처`로 우회 표현을 선택해, 평가 기준상 region slot hit가 1개만 잡혔습니다.

## 7. 결론

- `gpt-5-mini`는 길이 constraint를 잘 따릅니다.
- 다만 region 관련 조건은 `적게 쓰라`보다 `정확히 어디에 한 번 넣어라`처럼 더 명시적으로 써야 합니다.
- 즉 다음은 `region budget`보다 `region anchor`가 더 맞습니다.

## 8. 다음 액션

1. region을 `한 caption + 한 hashtag`에 정확히 넣도록 anchor 방식으로 바꿉니다.
2. `서울숲 근처` 같은 우회 표현을 허용할지, 아니면 평가상 `성수동` exact match를 계속 강제할지 결정해야 합니다.

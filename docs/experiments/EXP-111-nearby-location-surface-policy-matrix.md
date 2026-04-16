# EXP-111 Nearby-location surface policy matrix

## 1. 기본 정보

- 실험 ID: `EXP-111`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `policy matrix / nearby-location leakage / surface scope`

## 2. 왜 이 작업을 했는가

- `EXP-110`으로 nearby-location leakage를 자동 실패로 잡기 시작했지만, 아직 남은 질문이 있었습니다.
- `서울숲 근처`류를 정말 모든 surface에서 금지할지, 아니면 `captions/hashtags` 같은 distribution surface만 금지할지 정책 선택이 필요했습니다.
- 이번 작업은 기존 `EXP-108 repeatability` artifact를 surface 정책별로 다시 점수화해, 정책을 느슨하게 풀어도 모델 판단이 달라지는지 확인하는 단계입니다.

## 3. 비교한 정책

1. `strict_all_surfaces`
   - `hookText`, `ctaText`, `captions`, `hashtags`, `sceneText`, `subText`
2. `public_copy_surfaces`
   - `hookText`, `ctaText`, `captions`, `hashtags`, `sceneText`
3. `distribution_surfaces`
   - `captions`, `hashtags`

관련 draft manifest:

- `packages/template-spec/manifests/location-surface-policy-v1.json`

artifact:

- `docs/experiments/artifacts/exp-108-repeatability-location-policy-matrix.json`

## 4. 실행 결과

### Gemma 4

- 모든 정책에서 pass rate `1.0`
- leaked run: 없음

해석:

- `Gemma 4`는 strict all 기준에서도 leakage가 없었습니다.
- 즉 policy를 느슨하게 풀 필요가 없는 쪽입니다.

### GPT-5 Mini

- `strict_all_surfaces`
  - pass rate: `0.0`
  - avg leak count: `1.67`
- `public_copy_surfaces`
  - pass rate: `0.0`
  - avg leak count: `1.67`
- `distribution_surfaces`
  - pass rate: `0.0`
  - avg leak count: `1.67`

해석:

- `gpt-5-mini`는 정책을 풀어도 결과가 달라지지 않았습니다.
- 이유는 leakage가 이미 `captions`와 `hashtags`에서 발생했기 때문입니다.
  - run 1: `captions`
  - run 2: `captions`, `hashtags`
  - run 3: `captions`, `hashtags`

## 5. 결론

- 이번 matrix에서는 `느슨한 정책`으로 풀어도 결론이 바뀌지 않았습니다.
- 즉 현재 시점에서는:
  - `Gemma 4`는 strict policy에서도 안정적
  - `gpt-5-mini`는 distribution surface 수준에서도 leakage가 반복
- 따라서 기본 정책은 `strict_all_surfaces`로 두는 편이 맞습니다.

## 6. 정책 판단

1. `promotion / T02 / b_grade_fun` 기준 기본값은 `strict_all_surfaces`
2. 이유:
   - scene text/subText도 실제 결과물에 노출됨
   - 느슨한 정책으로 풀어도 `gpt-5-mini` 우위가 생기지 않음
   - `Gemma 4`는 strict all 기준에서도 이미 통과

## 7. 다음 액션

1. 현재 draft를 바탕으로 `copy-rule` 또는 `evaluation policy` 레이어에 위치 정책 필드를 넣을지 결정합니다.
2. 그 전까지는 strict region 실험에서 `strict_all_surfaces`를 임시 기본값으로 유지합니다.

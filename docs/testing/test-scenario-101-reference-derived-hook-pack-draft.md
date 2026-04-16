# Test Scenario 101 - reference-derived hook pack draft

## 목적

- `reference-hook-pack-v1.json`이 현재 템플릿의 hook slot에 실제로 매핑 가능한 후보군으로 기능하는지 확인합니다.

## 입력 자료

1. `packages/template-spec/manifests/slot-layer-map.json`
2. `packages/template-spec/manifests/reference-hook-pack-v1.json`
3. `docs/experiments/EXP-99-reference-derived-hook-pack-draft.md`

## 절차

1. `reference-hook-pack-v1.json`을 열어 10개 hook이 모두 `supportedTemplates`, `supportedPurposes`, `supportedStyles`를 가지는지 확인합니다.
2. 각 hook의 `requiredTokens`가 현재 프로젝트 입력 구조와 충돌하지 않는지 확인합니다.
3. `slot-layer-map.json`의 hook layer와 비교해, T01~T04에 실제로 연결 가능한지 점검합니다.
4. `templateFitClass`가 `template_fit_candidate` 또는 `partial_borrow`로 구분되어 있는지 확인합니다.

## 기대 결과

1. 현재 템플릿별로 바로 시험할 수 있는 hook 후보군이 생깁니다.
2. 기존 runtime을 바꾸지 않고도 hook 실험 backlog를 데이터 기준으로 정리할 수 있습니다.
3. 이후 copy generation 또는 editor UI 실험에 이 데이터를 연결할 수 있는 출발점이 됩니다.

## 판정 기준

- 아래 3개가 모두 맞으면 통과입니다.
  1. 모든 hook이 템플릿/목적/스타일 매핑을 가진다
  2. 토큰 구조가 현재 입력 모델과 크게 충돌하지 않는다
  3. production source of truth를 건드리지 않는 비파괴 draft다

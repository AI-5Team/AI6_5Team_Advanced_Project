# Test Scenario 100 - hook/body/CTA slot layer draft

## 목적

- `slot-layer-map.json`이 현재 템플릿 구조를 깨지 않으면서 `hook / body / cta` 레이어로 재해석하는 초안 역할을 하는지 확인합니다.

## 입력 자료

1. `packages/template-spec/templates/T01-new-menu.json`
2. `packages/template-spec/templates/T02-promotion.json`
3. `packages/template-spec/templates/T03-location-push.json`
4. `packages/template-spec/templates/T04-review.json`
5. `packages/template-spec/manifests/slot-layer-map.json`
6. `docs/experiments/EXP-98-hook-body-cta-slot-layer-draft.md`

## 절차

1. 각 템플릿의 `scenes[].textRole`를 읽습니다.
2. `slot-layer-map.json`의 `textRoleToLayer`를 읽습니다.
3. 템플릿별 `slotGroups` 매핑이 기존 scene 순서와 충돌하지 않는지 확인합니다.
4. `futureCopyPayloadDraft`가 현재 `hookText / captions[] / ctaText` 구조와 개념적으로 연결되는지 확인합니다.

## 기대 결과

1. 현재 템플릿 4종이 모두 `hook / body / cta` 레이어로 무리 없이 재해석됩니다.
2. 이 draft가 기존 runtime을 깨지 않는 비파괴 초안이라는 점이 분명합니다.
3. 다음 단계로 `hook pack`, `bodyBlocks`, `scene preview label` 논의를 이어갈 수 있습니다.

## 판정 기준

- 아래 3개가 모두 맞으면 통과입니다.
  1. 모든 템플릿에 hook/body/cta 매핑이 존재하는가
  2. 기존 template JSON을 수정하지 않고도 draft가 성립하는가
  3. 이후 copy/result 구조 확장 논의의 기반으로 쓸 수 있는가

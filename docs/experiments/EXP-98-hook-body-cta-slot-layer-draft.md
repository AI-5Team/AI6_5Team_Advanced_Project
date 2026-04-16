# EXP-98 Hook/body/CTA slot layer draft

## 1. 기본 정보

- 실험 ID: `EXP-98`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `template slot draft / hook-body-cta layer`

## 2. 왜 이 작업을 했는가

- 현재 템플릿은 이미 `scene slot`, `textRole`, `mediaRole` 기준으로 잘 쪼개져 있습니다.
- 하지만 외부 레퍼런스와 self-serve 제품 관점에서 보면, 다음 질문은 `이 템플릿이 hook/body/CTA 구조로 어떻게 읽히는가`입니다.
- 이번 작업의 목표는 기존 runtime을 깨지 않으면서, 현재 템플릿을 `hook / body / cta` 레이어로 다시 읽을 수 있는 비파괴 draft를 만드는 것입니다.

## 3. 무엇을 추가했는가

### 3.1 비파괴 manifest

- 파일: `packages/template-spec/manifests/slot-layer-map.json`
- 성격:
  - `draft-v1`
  - `nonBreaking = true`
  - 현재 runtime이 바로 소비하지는 않음
  - 기존 `templates/*.json`을 그대로 둔 상태에서, scene/textRole을 상위 레이어로 재매핑하는 초안

### 3.2 README 보강

- 파일: `packages/template-spec/README.md`
- 추가 내용:
  - `slot-layer-map.json`이 기존 스펙을 대체하지 않는 비파괴 draft라는 점

## 4. 현재 템플릿을 hook/body/CTA로 다시 읽으면

### T01 `신메뉴 티저형`

- hook:
  - `s1`
  - `textRole = hook`
- body:
  - `s2 = product_name`
  - `s3 = difference`
- cta:
  - `s4 = cta`

### T02 `오늘만 할인형`

- hook:
  - `s1 = hook`
- body:
  - `s2 = benefit`
  - `s3 = urgency`
- cta:
  - `s4 = cta`

### T03 `동네 방문 유도형`

- hook:
  - `s1 = region_hook`
- body:
  - `s2 = visit_reason`
  - `s3 = product_name`
- cta:
  - `s4 = cta`

### T04 `한줄 후기형`

- hook:
  - `s1 = review_quote`
- body:
  - `s2 = product_name`
- cta:
  - `s3 = cta`

## 5. 이 draft가 의미하는 것

### 5.1 지금 당장 바뀌는 것

- 아직 runtime은 바뀌지 않습니다.
- 하지만 이제 각 템플릿을 `scene 나열`이 아니라 `hook/body/cta 구성`으로 읽을 수 있습니다.
- 즉 템플릿 비교, 카피 설계, UI 라벨링, storyboard 설계 논의가 더 쉬워집니다.

### 5.2 다음 단계에서 바로 쓸 수 있는 것

1. `reference-derived hook pack`
   - 어떤 템플릿의 hook 자리에 어떤 문장을 꽂을지 명확해집니다.
2. `scene preview/storyboard`
   - 미리보기를 `hook block`, `body block`, `cta block` 기준으로 다시 보여줄 수 있습니다.
3. `copy deck`
   - 결과물을 `hookText`, `bodyBlocks[]`, `ctaText` 구조로 다시 정리할 수 있습니다.

## 6. future copy payload draft

- 이번 manifest에는 `futureCopyPayloadDraft`도 같이 넣었습니다.
- 의도:
  - 현재 `ProjectResultResponse.copySet`이 `hookText`, `captions[]`, `hashtags[]`, `ctaText` 중심이라면,
  - 이후에는 여기에 `bodyBlocks[]` 개념을 추가할 수 있는지 보는 초안입니다.

예상 방향:

```json
{
  "copyDeck": {
    "hook": {
      "primaryLineField": "hookText",
      "supportLineField": "captions[0]"
    },
    "body": {
      "blocksField": "bodyBlocks"
    },
    "cta": {
      "primaryLineField": "ctaText"
    }
  }
}
```

## 7. 지금 기준의 판단

- 현재 템플릿은 생각보다 이미 `hook/body/cta`에 가깝게 설계돼 있습니다.
- 그래서 다음은 템플릿 구조를 다시 만드는 것보다, `기존 템플릿을 그 관점으로 다시 라벨링하고 결과 payload를 그 구조로 노출하는 일`이 더 맞습니다.
- 즉 큰 구조 변경보다 `레이어 재해석 -> 결과 노출 정리 -> UI/preview 반영` 순서가 더 안전합니다.

## 8. 다음 우선순위

### 1순위

- `reference-derived hook pack`을 이 slot layer 기준으로 넣어 보기

### 2순위

- `bodyBlocks[]`를 문서 초안 수준에서 더 구체화하기

### 3순위

- result/history/scene preview에서 `hook/body/cta` 라벨을 실제로 노출할지 검토하기

## 9. 결론

- 이번 작업으로 `템플릿을 hook/body/cta 구조로 읽는 기준`이 생겼습니다.
- 이건 현재 본선 구조를 깨지 않으면서도, 이후 self-serve 광고 템플릿 방향으로 확장할 수 있는 가장 부담이 적은 첫 단계입니다.

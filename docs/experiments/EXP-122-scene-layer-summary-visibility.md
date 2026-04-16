# EXP-122 Scene Layer Summary Visibility

## 목적

- `copyDeck`이 결과 payload에 들어온 뒤, 각 scene이 `hook/body/cta` 중 무엇을 담당하는지 preview 단계에서도 바로 읽을 수 있게 합니다.

## 변경 범위

- `services/worker/pipelines/generation.py`
  - `slot-layer-map.json` 기준으로 `sceneLayerSummary`를 생성해 `render-meta.json`에 포함합니다.
- `services/api/app/services/runtime.py`
  - `/result` 응답에 `sceneLayerSummary`를 포함합니다.
- `apps/web/src/lib/demo-store.ts`
  - demo fallback result도 같은 `sceneLayerSummary`를 만듭니다.
- `apps/web/src/components/scene-plan-preview-links.tsx`
  - `sceneLayerSummary`를 받아 `s1 · HOOK · 후킹 문장` 같은 chip 형태로 보여줍니다.
- `apps/web/src/app/scene-frame/[scene]/page.tsx`
  - 현재 열려 있는 scene의 `slotGroup / uiLabel`을 in-frame overlay에 함께 표시합니다.

## 결과

- 이제 preview 카드와 scene-frame 모두에서 현재 scene이 `hook/body/cta` 중 어디에 속하는지 바로 읽을 수 있습니다.

## 판단

- `copyDeck`만 보여주면 문장 구조는 보이지만, 어떤 scene이 그 구조를 담당하는지는 다시 추론해야 했습니다.
- `sceneLayerSummary`를 넣으면서 result structure와 scene preview가 더 직접적으로 연결됐습니다.

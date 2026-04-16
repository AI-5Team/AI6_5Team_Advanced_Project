# EXP-121 Copy Deck Result Structure Visibility

## 목적

- `hook/body/cta`를 draft 문서에만 두지 않고, 실제 `result` payload와 결과 화면에서 보이게 합니다.
- 사용자가 현재 결과가 어떤 copy deck 구조로 배치됐는지 바로 읽을 수 있게 합니다.

## 변경 범위

- `services/worker/pipelines/generation.py`
  - `slot-layer-map.json` 기준으로 `copyDeck`를 생성해 `render-meta.json`에 추가했습니다.
- `services/api/app/services/runtime.py`
  - `/api/projects/{projectId}/result` 응답에 `copyDeck`를 포함합니다.
- `apps/web/src/lib/demo-store.ts`
  - demo fallback result도 같은 `copyDeck` shape를 생성합니다.
- `apps/web/src/components/copy-deck-summary.tsx`
  - `hook / body / cta` 구조를 읽는 결과 카드 컴포넌트를 추가했습니다.
- `apps/web/src/components/demo-workbench.tsx`
- `apps/web/src/components/history-board.tsx`
  - 결과/이력 화면 모두 `copyDeck`를 직접 노출합니다.

## 결과

- 이제 `result` payload는 `copySet`뿐 아니라 `copyDeck`도 같이 가집니다.
- 따라서 결과 화면에서 `hookText` 한 줄만 보는 것이 아니라, body block과 cta까지 템플릿 슬롯 기준으로 다시 읽을 수 있습니다.

## 판단

- 이 구조는 이후 `hook pack`이나 `bodyBlocks` 고도화를 실제 제품 payload에 연결하는 첫 단계입니다.
- 아직 draft 수준이지만, `hook/body/cta`를 제품 구조 안으로 끌어들였다는 의미가 큽니다.

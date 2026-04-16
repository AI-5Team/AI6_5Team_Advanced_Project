# 테스트 시나리오 24 - Scene Plan Web Bridge

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-24`

## 2. 테스트 목적

- `scene-frame`이 실제 prompt experiment artifact의 `scene_plan`을 읽어 렌더하는지 확인합니다.
- `scenePlan -> web -> PNG capture` 경로가 실제로 동작하는지 검증합니다.

## 3. 수행 항목

1. `npm run check`
2. `node scripts/capture_scene_plan_frames.mjs`
3. 생성된 PNG 및 `summary.json` 확인

## 4. 결과

- `npm run check`: 통과
- capture script: 통과
- 생성 artifact:
  - `promotion-opening.png`
  - `promotion-closing.png`
  - `review-region-opening.png`
  - `review-cta-closing.png`
  - `summary.json`

## 5. 관찰 내용

1. `scene-frame`이 `?artifact=` query로 실제 prompt experiment artifact를 읽어 렌더합니다.
2. `/api/local-media` route를 통해 `docs/sample` 이미지를 안전하게 읽을 수 있습니다.
3. 이제 hardcoded scene만이 아니라 실제 생성 카피가 포함된 frame PNG를 바로 비교할 수 있습니다.

## 6. 실패/제약

1. 스크립트 초안은 `next start` 작업 디렉터리 문제로 한 번 실패했습니다.
2. 현재는 experiment artifact 기준이고, production result API 직접 연결은 아직 아닙니다.

## 7. 개선 포인트

1. 다음은 `result.scenePlan`을 web이 직접 소비하도록 연결합니다.
2. 이후 worker run 단위 capture로 확장합니다.

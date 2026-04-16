# 테스트 시나리오 25 - Project Result ScenePlan Web Bridge

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-25`

## 2. 테스트 목적

- 실제 `projectId` 기준 생성 결과의 `result.scenePlan.url`을 web이 직접 읽는지 확인합니다.
- `project 생성 -> scenePlan fetch -> scene-frame capture` 경로가 실제로 재현되는지 검증합니다.

## 3. 수행 항목

1. `npm run check`
2. `node scripts/capture_project_scene_plan_frames.mjs`
3. 생성된 PNG 및 `summary.json` 확인

## 4. 결과

- `npm run check`: 통과
- capture script: 통과
- 생성 artifact:
  - `promotion-opening.png`
  - `promotion-closing.png`
  - `review-opening.png`
  - `review-closing.png`
  - `summary.json`

## 5. 관찰 내용

1. `scene-frame`이 `?projectId=` query로 실제 project result의 `scenePlan.url`을 따라갑니다.
2. local demo store에서도 `scenePlan`과 asset preview route가 연결돼 결과 확인 surface를 재현할 수 있습니다.
3. `promotion`, `review` 두 템플릿 모두에서 opening/closing frame 캡처가 가능합니다.

## 6. 실패/제약

1. local demo scenePlan은 worker Python output과 1:1 byte 동일한 파일은 아닙니다.
2. visual quality 자체를 검증한 테스트가 아니라, 연결 경로를 검증한 테스트입니다.

## 7. 개선 포인트

1. 다음은 result/history 화면이 `scenePlan` preview를 더 직접 노출하도록 연결합니다.
2. 이후 prompt/model OVAT 실험은 이 `projectId` 기반 bridge를 기준으로 다시 붙입니다.

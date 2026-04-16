# 테스트 시나리오 15 - Scene Frame Capture 검증

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-15`

## 2. 테스트 목적

- `/scene-frame/[scene]` route가 실제 headless browser screenshot 대상으로 동작하는지 검증합니다.
- scene artifact가 파일로 저장되고, 재현 가능한 summary까지 남는지 확인합니다.

## 3. 사전 조건

- `apps/web` build 가능 상태
- 로컬 Chrome 또는 Edge 실행 파일 존재
- `docs/sample` 샘플 사진 존재

## 4. 수행 항목

1. `node scripts/capture_scene_lab_frames.mjs`
2. `docs/experiments/artifacts/exp-11-html-css-scene-capture/` 생성 여부 확인
3. `scene-opening.png`, `scene-closing.png`, `summary.json` 생성 여부 확인
4. `npm run check`

## 5. 결과

- capture script: 통과
- 생성 artifact:
  - `scene-opening.png`
  - `scene-closing.png`
  - `summary.json`
  - `server.log`
- 전체 검증: `npm run check` 통과

## 6. 관찰 내용

1. HTML/CSS scene가 독립 route에서 실제 이미지 파일로 캡처됐습니다.
2. build, start, capture, artifact summary 저장까지 한 번에 재현 가능한 경로가 생겼습니다.
3. `/scene-frame/[scene]`는 nav 없는 전용 capture surface로 동작했습니다.

## 7. 실패/제약

1. visual quality는 개선됐지만 closing scene typography는 아직 polish가 필요합니다.
2. 이번 검증은 `web capture path` 기준이며, worker video pipeline 이식은 아직 아닙니다.

## 8. 개선 포인트

1. scene별 copy budget을 먼저 고정합니다.
2. opening / closing scene typography와 spacing을 추가 보정합니다.
3. 이후 worker render path 연결 여부를 결정합니다.

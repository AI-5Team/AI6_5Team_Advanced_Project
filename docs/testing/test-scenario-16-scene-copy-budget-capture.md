# 테스트 시나리오 16 - Scene Copy Budget Capture 검증

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-16`

## 2. 테스트 목적

- `opening / review / closing` scene에 copy budget과 type scale을 적용한 뒤, 실제 capture 결과가 무너지지 않는지 확인합니다.
- 포트 충돌 없이 항상 최신 build를 캡처하는지도 함께 검증합니다.

## 3. 사전 조건

- `apps/web` build 가능 상태
- 로컬 Chrome 또는 Edge 실행 파일 존재
- `docs/sample` 사진 존재

## 4. 수행 항목

1. `node scripts/capture_scene_lab_frames.mjs`
2. `summary.json`의 `baseUrl`이 실제 사용 포트로 기록되는지 확인
3. `scene-opening.png`, `scene-review.png`, `scene-closing.png` 3종 생성 여부 확인
4. capture 결과를 시각 확인
5. `npm run check`

## 5. 결과

- capture script: 통과
- 생성 artifact:
  - `scene-opening.png`
  - `scene-review.png`
  - `scene-closing.png`
  - `summary.json`
  - `server.log`
- 전체 검증: `npm run check` 통과

## 6. 관찰 내용

1. scene type별 copy budget이 적용되면서 headline/cta 무너짐은 크게 줄었습니다.
2. `review` scene도 독립 frame으로 정상 캡처됐습니다.
3. 포트 자동 선택이 적용되면서 이전 build를 잘못 재사용하는 문제가 사라졌습니다.

## 7. 실패/제약

1. `closing` scene의 body/kicker는 안전하지만 아직 존재감이 약합니다.
2. subcopy richness보다 layout integrity를 우선한 상태라, 다음 polish가 더 필요합니다.

## 8. 개선 포인트

1. bottom panel 비율과 subcopy hierarchy를 조정합니다.
2. review형 scene의 proof 표현을 더 설득력 있게 다듬습니다.

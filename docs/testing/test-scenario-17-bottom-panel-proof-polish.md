# 테스트 시나리오 17 - Bottom Panel / Proof Hierarchy Polish 검증

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-17`

## 2. 테스트 목적

- `closing` bottom panel과 `review` proof hierarchy를 다듬은 뒤, 실제 capture 결과에서 정보 우선순위가 더 자연스러운지 확인합니다.

## 3. 사전 조건

- `node scripts/capture_scene_lab_frames.mjs` 실행 가능
- 샘플 이미지 API 및 `/scene-frame/[scene]` route 정상 동작

## 4. 수행 항목

1. `node scripts/capture_scene_lab_frames.mjs`
2. `scene-review.png`, `scene-closing.png` 시각 확인
3. `npm run check`

## 5. 결과

- capture script: 통과
- 시각 확인:
  - `review` body가 proof block처럼 더 잘 보임
  - `closing` body/kicker hierarchy가 이전보다 분리됨
- 전체 검증: `npm run check` 통과

## 6. 관찰 내용

1. layout stability를 해치지 않으면서도 설명층의 존재감을 일부 되살렸습니다.
2. `closing`은 안전성을 유지한 채 설득력을 조금 더 복구했습니다.

## 7. 실패/제약

1. 아직 worker render path와 연결되지 않았습니다.
2. 장면 수가 적어 실제 서비스 다양성 검증은 더 필요합니다.

## 8. 개선 포인트

1. 동일 scene 구조를 더 많은 메뉴 사진으로 검증합니다.
2. 그 다음 worker 이식 또는 motion 실험으로 넘어갑니다.

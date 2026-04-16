# 테스트 시나리오 26 - History ScenePlan Preview

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-26`

## 2. 테스트 목적

- `history` 화면에서도 `scenePlan` preview 링크가 실제로 보이는지 확인합니다.
- 기본 선택 프로젝트가 result-ready 항목을 우선 고르는지 검증합니다.

## 3. 수행 항목

1. `npm run check`
2. `node scripts/capture_history_scene_plan_preview.mjs`
3. 생성된 screenshot과 `summary.json` 확인

## 4. 결과

- `npm run check`: 통과
- capture script: 통과
- 생성 artifact:
  - `history-scene-plan.png`
  - `summary.json`

## 5. 관찰 내용

1. `history` 화면에서 `scenePlan 미리보기` block이 실제로 렌더됩니다.
2. opening/closing scene 링크가 같은 `projectId` 기준으로 구성됩니다.
3. 기본 선택 프로젝트가 `published` 같은 result-ready 상태를 먼저 고르도록 조정돼, 첫 진입에서 결과가 비어 보이는 문제가 줄었습니다.

## 6. 실패/제약

1. 최초 구현은 기본 선택이 `generating` 프로젝트여서 preview block이 보이지 않았습니다.
2. 이 테스트는 링크 노출 확인까지이며, 클릭 후 장면 비교 UX 자체는 별도 과제입니다.

## 7. 개선 포인트

1. 다음은 history에서도 복수 result 비교가 가능한 최소 비교 view를 고민합니다.
2. 이후 prompt/model 실험은 이 history/main 공통 preview 경로를 기준으로 다시 진행합니다.

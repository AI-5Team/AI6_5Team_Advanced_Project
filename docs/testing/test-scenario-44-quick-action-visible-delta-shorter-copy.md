# 테스트 시나리오 44 - Quick Action Visible Delta (shorterCopy)

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-44`

## 2. 테스트 목적

- 실제 프로젝트 생성 후 `문구 더 짧게(shorterCopy)`가 regenerate 결과에 눈에 띄는 차이를 만드는지 확인합니다.

## 3. 수행 항목

1. `node scripts/capture_quick_action_delta.mjs`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-41-quick-action-visible-delta/summary.json`
  - `baseline-opening.png`
  - `shorter-copy-opening.png`

## 5. 관찰 내용

1. hookText 길이가 `11자` 줄었습니다.
2. opening scene에서 문구가 실제로 더 짧아졌습니다.
3. 처음에는 zero-delta였지만, 원인을 수정한 뒤 재실행에서 정상 동작을 확인했습니다.

## 6. 실패/제약

1. 최초 점검에서는 web demo regenerate와 scene-frame preview 경로 버그가 있었습니다.
2. 이번 테스트는 검증과 버그 수정이 함께 진행된 케이스입니다.

## 7. 개선 포인트

1. 다음 quick action도 같은 방식으로 visible delta를 검증해야 합니다.
2. 특히 `highlightPrice`와 `emphasizeRegion` 우선 검증이 적절합니다.

# 테스트 시나리오 56 - history latest publish attempt

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-56`

## 2. 테스트 목적

- 같은 프로젝트에서 게시를 두 번 시도했을 때 history 화면이 최신 시도를 기준으로 상태를 보여주는지 확인합니다.

## 3. 수행 항목

1. `node scripts/capture_history_latest_publish_attempt.mjs`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-53-history-latest-publish-attempt/summary.json`
  - `history-latest-publish-status.png`

## 5. 관찰 내용

1. 첫 번째 `instagram auto publish`는 정상적으로 `published`가 됐습니다.
2. 두 번째 `tiktok auto publish`는 `assist_required`로 전환됐습니다.
3. history 화면은 첫 번째 성공이 아니라 두 번째 fallback을 최신 상태로 보여줬습니다.

## 6. 실패/제약

1. local demo publish state machine 검증입니다.
2. 복수 publish job의 목록 비교 UI까지는 아직 없습니다.

## 7. 개선 포인트

1. 복수 시도가 많아질 경우 timeline/list가 필요한지 따로 판단해야 합니다.
2. runtime/API 쪽에도 시간이 노출되도록 contract를 맞출지 검토합니다.

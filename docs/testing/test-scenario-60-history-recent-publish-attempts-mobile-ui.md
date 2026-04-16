# 테스트 시나리오 60 - history recent publish attempts mobile UI

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-60`

## 2. 테스트 목적

- recent attempts 요약이 모바일 폭에서도 실제로 읽히는지 확인합니다.

## 3. 수행 항목

1. `node scripts/capture_history_recent_publish_attempts_mobile_ui.mjs`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-57-history-recent-publish-attempts-mobile-ui/summary.json`
  - `history-recent-publish-attempts-mobile.png`

## 5. 관찰 내용

1. `최근 게시 시도 2회`와 최근 2건 요약이 모바일에서도 읽힙니다.
2. 최신 `tiktok assist_required`와 이전 `instagram published`가 한 칼럼 흐름에서 구분됩니다.
3. 구조 붕괴나 치명적 겹침은 보이지 않았습니다.

## 6. 실패/제약

1. 실기기 브라우저 검증은 아닙니다.
2. 430px 기준 1회 확인입니다.

## 7. 개선 포인트

1. 더 작은 폭과 실기기 safe-area는 나중에 따로 확인합니다.
2. 본선은 history보다 publish/package 전체 흐름 연결 검증으로 다시 넘어갈 수 있습니다.

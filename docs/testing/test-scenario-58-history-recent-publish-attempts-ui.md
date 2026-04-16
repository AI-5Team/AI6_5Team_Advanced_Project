# 테스트 시나리오 58 - history recent publish attempts UI

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-58`

## 2. 테스트 목적

- 같은 프로젝트에서 게시를 두 번 시도했을 때 history 화면이 최근 시도들을 이해 가능한 수준으로 보여주는지 확인합니다.

## 3. 수행 항목

1. `node scripts/capture_history_recent_publish_attempts_ui.mjs`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-55-history-recent-publish-attempts-ui/summary.json`
  - `history-recent-publish-attempts.png`

## 5. 관찰 내용

1. history detail panel에 `최근 게시 시도 2회`가 표시됩니다.
2. 최신 `tiktok assist_required`와 이전 `instagram published`가 함께 보입니다.
3. 따라서 복수 시도 상황에서 latest 상태의 맥락이 훨씬 잘 설명됩니다.

## 6. 실패/제약

1. local demo publish state machine 검증입니다.
2. full timeline UI는 아직 없습니다.

## 7. 개선 포인트

1. 모바일 화면에서 최근 시도 요약이 충분히 읽히는지 다음에 확인합니다.
2. runtime/API와 동일 개념으로 정렬할지 검토합니다.

# 테스트 시나리오 53 - history publish 상태 가시성

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-53`

## 2. 테스트 목적

- history 화면에서 `instagram permission_error -> assist fallback`의 최신 게시 상태와 이유가 실제로 보이는지 확인합니다.

## 3. 수행 항목

1. `node scripts/capture_history_publish_status_visibility.mjs`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-50-history-publish-status-visibility/summary.json`
  - `history-publish-status.png`

## 5. 관찰 내용

1. history 화면이 `projectId` query로 대상 프로젝트를 바로 선택합니다.
2. detail panel에서 `instagram · 보조 필요`와 `업로드 보조 모드로 전환되었습니다.` 메시지가 함께 보입니다.
3. `업로드 보조 패키지 준비됨`도 같이 보여서, 게시 실패 후 이어서 작업할 맥락이 유지됩니다.

## 6. 실패/제약

1. local demo publish state machine 검증입니다.
2. 복수 upload job이 누적된 상태에서 최신 선택 기준까지는 아직 보지 않았습니다.

## 7. 개선 포인트

1. 다음에는 history 화면에서 `최근 게시 시도 시각`까지 같이 보여줄지 검토합니다.
2. 복수 publish job이 있을 때 timeline 또는 이력 카드가 필요한지 확인합니다.

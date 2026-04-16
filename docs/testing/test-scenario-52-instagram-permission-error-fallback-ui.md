# 테스트 시나리오 52 - Instagram permission_error Fallback UI

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-52`

## 2. 테스트 목적

- `instagram permission_error -> assist fallback`이 실제 UI 카드에 보이는지 확인합니다.

## 3. 수행 항목

1. `node scripts/capture_instagram_permission_error_fallback_ui.mjs`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-49-instagram-permission-error-fallback-ui/summary.json`
  - `instagram-permission-error-home.png`

## 5. 관찰 내용

1. `instagram` 계정이 `permission_error` 상태가 되면 자동 게시 대신 `assist_required`로 전환됩니다.
2. 결과/게시 카드에서 `보조 필요` 상태와 fallback 메시지가 같이 보입니다.
3. 따라서 실패 전환 경로도 사용자 눈에 드러납니다.

## 6. 실패/제약

1. 외부 Instagram API 실환경 검증은 아닙니다.
2. local demo state machine 기준 재현입니다.

## 7. 개선 포인트

1. 다음에는 history/result 화면도 같은 publish 상태 가시성을 제공하는지 봐야 합니다.
2. runtime/API 쪽 메시지와 web 표시 문구도 계속 맞춰야 합니다.

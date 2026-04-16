# EXP-57 History recent publish attempts mobile UI

## 1. 기본 정보

- 실험 ID: `EXP-57`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `서비스 본선 history/result 모바일 가독성`

## 2. 왜 이 작업을 했는가

- `EXP-55`에서 desktop 기준으로 recent attempts 요약이 유효하다는 것은 확인했습니다.
- 하지만 최근 시도 카드가 모바일 폭에서도 읽히지 않으면 본선 기준으로는 절반짜리 검증이라, 모바일 캡처를 따로 확인해야 했습니다.

## 3. baseline

### 고정한 조건

1. 경로: `web demo local server`
2. 업종/목적/스타일: `restaurant / promotion / b_grade_fun`
3. 템플릿: `T02`
4. 같은 프로젝트에서 게시를 두 번 시도
   - `instagram auto success`
   - `tiktok auto fallback`
5. 모바일 viewport: `430 x 2600`

## 4. 무엇을 바꿨는가

- 검증용 스크립트 `scripts/capture_history_recent_publish_attempts_mobile_ui.mjs`를 추가했습니다.
- 이번 실험에서는 UI 코드를 추가로 바꾸지 않고, 현재 recent attempts 요약이 모바일에서 그대로 읽히는지 먼저 확인했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-57-history-recent-publish-attempts-mobile-ui/summary.json`
- `docs/experiments/artifacts/exp-57-history-recent-publish-attempts-mobile-ui/history-recent-publish-attempts-mobile.png`

### baseline 대비 차이

- 모바일 화면에서:
  - 좌측 목록과 선택 프로젝트가 한 칼럼으로 정상 전환됩니다.
  - `최근 게시 시도 2회`
  - 최신 `tiktok · 보조 필요`
  - 이전 `instagram · 게시 완료`
  가 모두 한 화면 흐름 안에서 읽힙니다.

### 확인된 것

1. 현재 recent attempts 요약은 모바일에서도 구조 붕괴 없이 읽힙니다.
2. latest-only보다 recent attempts 요약이 모바일에서도 여전히 더 이해하기 쉽습니다.
3. 즉 recent attempts 요약은 desktop 전용 보조 기능이 아니라 본선에 유지할 가치가 있습니다.

## 6. 실패/제약

1. local demo publish state machine 검증입니다.
2. 이번 캡처는 430px 기준 1회 확인입니다.
3. 모바일에서 더 작은 폭이나 실기기 브라우저 safe-area까지 본 것은 아닙니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - recent attempts 요약은 모바일에서도 유지하는 편이 맞습니다.
  - 당장 별도 모바일 전용 UI를 더 만들 필요는 없어 보입니다.

## 8. 다음 액션

1. 실기기 브라우저 기준으로 safe-area와 sticky nav 충돌 여부를 나중에 확인합니다.
2. 본선은 이제 history보다 publish/package 전체 흐름과 생성 실험 결과 연결을 다시 보는 편이 맞습니다.

# EXP-55 History recent publish attempts UI

## 1. 기본 정보

- 실험 ID: `EXP-55`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `서비스 본선 history/result 복수 게시 시도 가시성`

## 2. 왜 이 작업을 했는가

- `EXP-53`에서 history가 최신 게시 시도를 잘 집어낸다는 것은 확인했습니다.
- 다만 사용자 입장에서는 왜 그 상태가 최신인지, 직전 시도와 어떻게 다른지 맥락이 부족했습니다.
- 그래서 이번에는 `최근 시도 목록`을 짧게 보여주는 UI가 실제로 필요한지 확인했습니다.

## 3. baseline

### 고정한 조건

1. 경로: `web demo local server`
2. 업종/목적/스타일: `restaurant / promotion / b_grade_fun`
3. 템플릿: `T02`
4. 자산: `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg`
5. 같은 프로젝트에서 게시를 두 번 시도

### 시도 순서

1. 1차 시도: `instagram auto publish`
2. 2차 시도: `tiktok auto publish`

## 4. 무엇을 바꿨는가

- same-origin demo route를 추가했습니다.
  - `GET /api/projects/[projectId]/upload-jobs`
- history 화면을 보강했습니다.
  - 최근 게시 시도 개수 표시
  - 최신 시도와 이전 시도 1건을 요약 카드로 표시
  - `현재 표시 중인 최신 시도` 라벨 추가
- 검증용 스크립트 `scripts/capture_history_recent_publish_attempts_ui.mjs`를 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-55-history-recent-publish-attempts-ui/summary.json`
- `docs/experiments/artifacts/exp-55-history-recent-publish-attempts-ui/history-recent-publish-attempts.png`

### baseline 대비 차이

- 이전
  - latest 상태만 보여서 왜 이 상태가 최신인지 설명이 약했습니다.
- 이후
  - `최근 게시 시도 2회`
  - `현재 표시 중인 최신 시도 · tiktok · 보조 필요`
  - `이전 시도 · instagram · 게시 완료`
  를 한 화면에서 확인할 수 있습니다.

### 확인된 것

1. 복수 게시 시도가 쌓이면 latest-only보다 짧은 최근 시도 요약이 훨씬 이해가 쉽습니다.
2. 사용자는 최신 fallback과 이전 성공 시도를 동시에 보고 맥락을 파악할 수 있습니다.
3. history 화면의 publish 맥락 설명력이 한 단계 올라갔습니다.

## 6. 실패/제약

1. local demo publish state machine 기준입니다.
2. 현재는 최근 3건까지만 요약하고, 별도 timeline 페이지는 없습니다.
3. 외부 runtime/API 쪽에 동일 route가 있는 것은 아닙니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 복수 publish 시도 상황에서는 latest-only보다 최근 시도 요약이 필요합니다.
  - 현재 수준에서는 full timeline보다 최근 2~3건 요약이 비용 대비 적절합니다.

## 8. 다음 액션

1. runtime/API 쪽에도 같은 개념이 필요하면 contract 정렬을 검토합니다.
2. 그 다음 본선은 `최근 시도 요약`이 모바일에서도 충분히 읽히는지 확인합니다.

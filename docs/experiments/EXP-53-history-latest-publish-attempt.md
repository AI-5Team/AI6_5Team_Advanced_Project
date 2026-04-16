# EXP-53 History latest publish attempt selection

## 1. 기본 정보

- 실험 ID: `EXP-53`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `서비스 본선 history/result 최신 게시 시도 가시성`

## 2. 왜 이 작업을 했는가

- `EXP-50`에서 history 화면이 최신 publish 상태를 보여주도록 보강했습니다.
- 하지만 실제로 한 프로젝트에서 게시를 두 번 시도했을 때
  - 이전 성공 시도
  - 이후 fallback 시도
  중 어떤 것을 history가 보여주는지 확인해야 했습니다.

## 3. baseline

### 고정한 조건

1. 경로: `web demo local server`
2. 업종/목적/스타일: `restaurant / promotion / b_grade_fun`
3. 템플릿: `T02`
4. 자산: `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg`
5. 같은 프로젝트에서 publish를 두 번 시도

### 시도 순서

1. 1차 시도: `instagram auto publish`
2. 2차 시도: `tiktok auto publish`

## 4. 무엇을 바꿨는가

- `UploadJobResponse`에 시간 정보를 노출했습니다.
  - `createdAt`
  - `updatedAt`
  - `publishedAt`
- history detail panel에 `최근 시도` 시각을 표시했습니다.
- 검증용 스크립트 `scripts/capture_history_latest_publish_attempt.mjs`를 추가했습니다.
  - 동일 프로젝트 생성/생성 완료
  - 1차 `instagram auto success`
  - 2차 `tiktok auto fallback`
  - `/history?projectId=...` 캡처

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-53-history-latest-publish-attempt/summary.json`
- `docs/experiments/artifacts/exp-53-history-latest-publish-attempt/history-latest-publish-status.png`

### baseline 대비 차이

- 1차 시도
  - channel: `instagram`
  - status: `published`
- 2차 시도
  - channel: `tiktok`
  - status: `assist_required`
  - error: `SOCIAL_TOKEN_EXPIRED`
- latest route
  - latest upload job id가 2차 시도와 일치했습니다.
  - history 화면에도 `tiktok · 보조 필요`, `토큰이 만료되어 재연동이 필요합니다.`가 표시됐습니다.

### 확인된 것

1. history는 오래된 성공 시도가 아니라 최신 fallback 시도를 보여줍니다.
2. `최근 시도` 시각이 붙어서 왜 이 카드가 최신인지 설명이 더 분명해졌습니다.
3. 한 프로젝트에서 게시를 여러 번 시도해도 최신 상태 기준으로 이어서 작업할 수 있습니다.

## 6. 실패/제약

1. local demo publish state machine 기준입니다.
2. 아직 history는 복수 publish 시도 목록 자체를 보여주지는 않습니다.
3. 시간 정보는 demo same-origin route 기준이며, 외부 API 응답 스키마에는 아직 강제되어 있지 않습니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 현재 history는 복수 publish 시도 상황에서도 최신 작업을 제대로 집어냅니다.
  - 다음 본선 검증은 publish 시도 목록이 필요한지, 아니면 최신 상태만으로 충분한지 판단하는 쪽이 맞습니다.

## 8. 다음 액션

1. 복수 publish 시도가 쌓일 때 timeline/list가 실제로 필요한지 UX 기준으로 검토합니다.
2. runtime/API 쪽에도 시간 정보가 필요하면 contract 정렬을 별도로 진행합니다.

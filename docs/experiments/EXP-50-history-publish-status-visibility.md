# EXP-50 History publish 상태 가시성

## 1. 기본 정보

- 실험 ID: `EXP-50`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `서비스 본선 history/result publish 상태 가시성`

## 2. 왜 이 작업을 했는가

- `EXP-49`에서 메인 화면은 `instagram permission_error -> assist fallback` 이유를 바로 보여주도록 정리했습니다.
- 하지만 history/result 화면은 여전히 프로젝트 상태와 결과 요약만 보여주고, 최근 게시 실패 이유나 보조 전환 여부는 바로 확인하기 어려웠습니다.
- 따라서 이번에는 history 화면에서도 최신 publish 경로가 눈에 보이는지 확인해야 했습니다.

## 3. baseline

### 고정한 조건

1. 경로: `web demo local server`
2. 업종/목적/스타일: `restaurant / promotion / b_grade_fun`
3. 템플릿: `T02`
4. 자산: `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg`
5. 게시 채널: `instagram`
6. 게시 모드: `auto`
7. 실패 시나리오: `connect -> callback(permission-error) -> auto publish`

### baseline 문제

1. history 화면은 최신 upload job을 보여주지 않았습니다.
2. 특정 프로젝트를 history에서 바로 열어도 publish fallback 이유를 확인할 수 없었습니다.

## 4. 무엇을 바꿨는가

- `HistoryBoard`를 보강했습니다.
  - `initialProjectId` prop과 `history?projectId=` query로 특정 프로젝트를 우선 선택하도록 변경
  - 최신 upload job을 별도로 로드
  - `채널 / 상태 / fallback 메시지 / assist package 준비 여부`를 detail panel에 노출
  - 메인 화면 복귀 링크에 `uploadJobId`를 같이 붙여 publish 작업을 바로 이어가도록 정리
- same-origin demo route를 추가했습니다.
  - `GET /api/projects/[projectId]/latest-upload-job`
  - `demo-store.ts`에 `getLatestUploadJobForProject()` 추가
- 검증용 스크립트 `scripts/capture_history_publish_status_visibility.mjs`를 추가했습니다.
  - `instagram permission-error`
  - 프로젝트 생성/자산 업로드/생성/게시
  - `/history?projectId=...` 캡처

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-50-history-publish-status-visibility/summary.json`
- `docs/experiments/artifacts/exp-50-history-publish-status-visibility/history-publish-status.png`

### baseline 대비 차이

- 상태 노출
  - 이전: `upload_assist` 또는 `published` 같은 프로젝트 상태만 간접적으로 확인 가능
  - 이후: `instagram · 보조 필요`, `업로드 보조 모드로 전환되었습니다.` 메시지, `업로드 보조 패키지 준비됨`을 detail panel에서 직접 확인 가능
- 진입 경로
  - 이전: history가 어떤 프로젝트를 선택할지 목록 순서에 의존
  - 이후: `history?projectId=<id>`로 대상 프로젝트를 고정 가능
- 이어서 작업
  - 이전: 메인 화면으로 돌아가면 publish context가 끊김
  - 이후: `uploadJobId`를 같이 넘겨 publish 상태를 이어서 확인 가능

### 확인된 것

1. history 화면에서도 `assist_required` 상태와 fallback 이유가 눈에 보입니다.
2. `projectId` query 기반으로 동일 프로젝트를 재현 가능해져서 publish 상태 검증이 안정화됐습니다.
3. 메인 화면과 history 화면의 publish 맥락이 하나의 `uploadJobId`로 연결됩니다.

## 6. 실패/제약

1. 이번 검증은 local demo state machine 기준입니다.
2. 최신 upload job route는 현재 demo same-origin 경로에만 있습니다.
3. history 화면은 아직 복수 publish job 비교나 publish timeline까지는 보여주지 않습니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - history/result 화면도 이제 publish 실패 전환을 확인할 수 있는 수준까지 올라왔습니다.
  - 본선에서는 다음으로 success/fallback이 아닌 `여러 게시 시도 중 최신 상태`를 얼마나 잘 설명하는지까지 보면 됩니다.

## 8. 다음 액션

1. history 화면에서 복수 publish 시도가 생겼을 때 최신 기준이 충분히 명확한지 봅니다.
2. publish timeline 또는 최근 시도 시각을 붙일지 검토합니다.

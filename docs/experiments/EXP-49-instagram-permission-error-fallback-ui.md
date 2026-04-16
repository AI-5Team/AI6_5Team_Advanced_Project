# EXP-49 Instagram permission_error Fallback UI

## 1. 기본 정보

- 실험 ID: `EXP-49`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `서비스 본선 게시 실패 fallback / UI 가시성`

## 2. 왜 이 작업을 했는가

- `EXP-47`에서 게시 경로 matrix는 API 상태 기준으로 검증했습니다.
- 하지만 실제 사용자 관점에서는 `instagram permission_error`가 발생했을 때
  - fallback이 트리거되는지
  - 그 이유가 UI에 보이는지
  까지 확인해야 합니다.

## 3. baseline

### 고정한 조건

1. 경로: `web demo local server`
2. 업종/목적/스타일: `restaurant / promotion / b_grade_fun`
3. 템플릿: `T02`
4. 자산: `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg`
5. 게시 채널: `instagram`
6. 게시 모드: `auto`

### 이번 점검 항목

1. `instagram connect -> callback(permission-error)` 후 상태 유지
2. `auto publish`가 `assist_required`로 전환되는지
3. fallback 이유가 UI 카드에 보이는지

## 4. 무엇을 바꿨는가

- 캡처 스크립트 `scripts/capture_instagram_permission_error_fallback_ui.mjs`를 추가했습니다.
- `DemoWorkbench`를 소폭 보강했습니다.
  - `uploadJobId` query param으로 특정 upload job을 바로 로드
  - publish 직후 `getUploadJob()`을 즉시 읽어 fallback 이유를 바로 표시
  - upload job 에러 메시지를 결과 카드에 노출
  - `assisted_completed` 상태를 positive tone으로 분류
- `demo-store.ts`도 runtime과 맞췄습니다.
  - `PUBLISH_FAILED` 메시지를 `업로드 보조 모드로 전환되었습니다.`로 통일

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-49-instagram-permission-error-fallback-ui/summary.json`
- `docs/experiments/artifacts/exp-49-instagram-permission-error-fallback-ui/instagram-permission-error-home.png`

### baseline 대비 차이

- OAuth callback
  - callback status: `400`
  - account degraded state: 유지됨
- publish
  - publish response status: `assist_required`
  - upload job error: `PUBLISH_FAILED`
  - upload job message: `업로드 보조 모드로 전환되었습니다.`
- UI
  - 결과/게시 카드에서 `보조 필요` 상태와 fallback 이유가 함께 노출됩니다.

### 확인된 것

1. `instagram permission_error`는 현재 데모 기준선에서 실제로 fallback으로 전환됩니다.
2. fallback 이유가 UI 카드에 바로 보이도록 정리됐습니다.
3. `uploadJobId` query 기반 로드가 가능해져서, 특정 게시 상태를 재현/검증하기 쉬워졌습니다.

## 6. 실패/제약

1. 이번 검증은 외부 Instagram API가 아니라 local demo state machine 기준입니다.
2. callback은 의도적으로 `400`을 반환하지만, degraded account state는 내부 store에 남도록 설계된 경로입니다.
3. UI 스크린샷은 디버그성 재현 경로(`projectId`, `uploadJobId` query) 기준입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `instagram permission_error -> assist fallback`은 API/상태/UI까지 모두 연결된 경로로 재현 가능합니다.
  - 이제 publish 본선은 성공 경로뿐 아니라 실패 전환 경로도 사용자 눈에 보이는 수준까지 올라왔습니다.

## 8. 다음 액션

1. 다음 본선 검증은 history/result 화면에서 publish 상태 차이가 얼마나 잘 보이는지 점검하는 편이 맞습니다.
2. 이후에는 실제 runtime 쪽도 동일한 메시지 체계를 유지하는지 다시 교차 확인해야 합니다.

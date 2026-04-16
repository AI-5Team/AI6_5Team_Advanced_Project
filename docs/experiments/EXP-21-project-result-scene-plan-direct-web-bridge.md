# EXP-21 Project Result ScenePlan Direct Web Bridge

## 1. 기본 정보

- 실험 ID: `EXP-21`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `project result.scenePlan -> web -> scene-frame -> PNG capture`

## 2. 왜 이 작업을 했는가

- `EXP-20`까지는 prompt experiment artifact의 `scene_plan`을 web에서 읽는 bridge만 연결돼 있었습니다.
- 하지만 서비스 기획 기준으로 더 중요한 경로는 `실제 프로젝트 생성 결과(result.scenePlan)`를 web surface가 직접 소비하는 것입니다.
- 즉, 이번 작업의 목적은 “artifact 기반 확인”에서 한 단계 더 나아가, 실제 `projectId` 기준 생성 결과가 `scene-frame`에 바로 연결되는지 검증하는 것이었습니다.

## 3. baseline

### 이전 baseline

1. `scene-frame`은 `?artifact=` query로 prompt experiment JSON만 읽었습니다.
2. web의 결과 화면은 `copySet`만 보여 주고, `result.scenePlan`은 직접 소비하지 않았습니다.
3. 즉, 생성 실험 결과와 web 확인 surface 사이에 여전히 한 단계의 수동 연결이 남아 있었습니다.

### 이번에 고정한 조건

1. web surface 자체는 기존 `scene-frame` poster renderer를 유지했습니다.
2. 바꾼 것은 renderer 스타일이 아니라 `scenePlan source` 하나입니다.
3. 검증 시나리오는 아래 두 개로 고정했습니다.
   - `T02 / promotion / b_grade_fun`
   - `T04 / review / b_grade_fun`

## 4. 무엇을 바꿨는가

### result 직접 소비 경로

- `apps/web/src/lib/contracts.ts`
  - `ProjectResultResponse.scenePlan` 타입 추가
- `apps/web/src/lib/demo-store.ts`
  - demo result에 `scenePlan.url` 메타 추가
  - `getProjectScenePlan(projectId)` 추가
  - 업로드 자산 preview binary를 메모리에 유지하도록 확장
- `apps/web/src/app/api/projects/[projectId]/scene-plan/route.ts`
  - local demo result용 `scenePlan` JSON route 추가
- `apps/web/src/app/api/projects/[projectId]/assets/[assetId]/preview/route.ts`
  - 업로드 자산 preview image route 추가
- `apps/web/src/lib/scene-plan.ts`
  - `loadProjectScenePlan(projectId, requestBaseUrl)` 추가
  - `NEXT_PUBLIC_API_BASE_URL`이 있으면 실제 backend base를 따라가도록 정리
- `apps/web/src/components/scene-lab.tsx`
  - `/api/*`, `/projects/*`, `/media/*` 자산 path를 실제 image src로 해석하도록 보강
- `apps/web/src/app/scene-frame/[scene]/page.tsx`
  - `?projectId=` query가 들어오면 `result.scenePlan.url`을 따라 실제 scenePlan을 불러오도록 수정
- `apps/web/src/components/demo-workbench.tsx`
  - 결과 패널에 `scenePlan 확인` 링크 추가

### 검증 스크립트

- `scripts/capture_project_scene_plan_frames.mjs`
  - web 서버를 띄운 뒤
  - 프로젝트 생성 -> 자산 업로드 -> generate 호출 -> status polling -> result/scenePlan fetch -> `scene-frame?projectId=` 캡처
  - 까지를 한 번에 재현하도록 추가했습니다.

## 5. 실행 결과

### 생성 및 캡처 결과

- 생성 artifact:
  - `docs/experiments/artifacts/exp-21-project-result-scene-plan-web-bridge/promotion-opening.png`
  - `docs/experiments/artifacts/exp-21-project-result-scene-plan-web-bridge/promotion-closing.png`
  - `docs/experiments/artifacts/exp-21-project-result-scene-plan-web-bridge/review-opening.png`
  - `docs/experiments/artifacts/exp-21-project-result-scene-plan-web-bridge/review-closing.png`
  - `docs/experiments/artifacts/exp-21-project-result-scene-plan-web-bridge/summary.json`

### 확인된 것

1. `scene-frame`이 더 이상 experiment artifact에만 의존하지 않고, 실제 `projectId` 기준 `result.scenePlan.url`을 직접 따라갑니다.
2. `promotion`, `review` 두 템플릿 모두에서 `scenePlan` route -> frame capture 경로가 통과했습니다.
3. `scene-lab`이 `/projects/*`나 local preview route를 해석할 수 있게 되어, backend scenePlan JSON을 따라갈 수 있는 형태가 됐습니다.
4. main workbench에서도 실제 결과 기준 scene 확인 링크를 노출할 수 있게 됐습니다.

## 6. 실패/제약

1. 이번 작업은 renderer 미감 개선이 아니라 `result 소비 경로` 복구입니다.
2. local demo store의 `scenePlan`은 worker Python 구현이 아니라 TypeScript mirror builder입니다.
3. 업로드 자산은 demo 환경에서 메모리 preview route로 서빙합니다. 실제 worker storage와 완전히 같은 구조는 아닙니다.
4. 캡처 결과를 보면 연결은 맞지만, visual quality 자체가 좋아졌다고 말할 단계는 아닙니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 이제 web이 “하드코딩된 샘플 장면”이나 “실험 artifact 파일”만 보던 상태는 벗어났습니다.
  - `project result.scenePlan`을 실제로 소비하는 경로가 생겼기 때문에, 이후 생성 실험을 다시 서비스 루프 기준으로 검증할 수 있습니다.

## 8. 다음 액션

1. 가능하면 같은 route를 `history/result` 화면까지 연결합니다.
2. `scenePlan` 기반 capture 결과와 prompt lever 결과를 같은 실험 보고서 안에서 묶어 비교합니다.
3. 그 다음 OVAT prompt/model 실험은 `실제 project result.scenePlan` 기준으로 다시 이어갑니다.

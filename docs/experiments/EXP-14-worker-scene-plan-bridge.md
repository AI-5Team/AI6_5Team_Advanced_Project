# EXP-14 Worker Scene Plan Bridge

## 1. 기본 정보

- 실험 ID: `EXP-14`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: worker/template-spec -> scene plan bridge, result API 연결

## 2. 왜 이 실험을 추가했는가

- `ADR-009` 기준으로, HTML/CSS renderer spike를 계속 키우는 대신 실제 생성 경로로 다시 돌아와야 했습니다.
- 그래서 이번에는 `scene-lab`을 더 예쁘게 다듬는 대신, worker가 실제 `template + style + copy bundle + processed assets`를 읽어 `scene-plan.json`을 내보내도록 연결했습니다.

## 3. baseline

- 기준선:
  - worker는 `scene image / video / post / caption / hashtags`만 만들고 있었음
  - web scene prototype은 hardcoded scene data로만 움직였음
- 한계:
  - worker 생성 결과와 web/capture 표면이 같은 장면 정의를 공유하지 않았음
  - 따라서 실제 생성이 왜 구린지 구조적으로 보기 어려웠음

## 4. 이번 실험에서 바꾼 것

1. `services/worker/planning/scene_plan.py`
   - template/spec/style/copy를 바탕으로 `scene-plan.json`을 만드는 bridge 추가
2. `services/worker/pipelines/generation.py`
   - generation run 중 `scene-plan.json` 저장
   - `render_meta`에 `scenePlanPath`, `sceneSpecVersion`, `sceneCount` 추가
3. `services/api/app/services/runtime.py`
   - `/api/projects/{projectId}/result` 응답에 `scenePlan` 링크 추가
4. `packages/contracts/schemas/generation.ts`
   - 결과 계약에 `scenePlan` 필드 추가
5. `scripts/export_scene_plan_samples.py`
   - 실제 worker generation path를 돌려 `T02`, `T04` 샘플 scene plan artifact 생성

## 5. 결과

### 확인된 것

1. 이제 worker 생성 결과가 `scene-plan.json`으로도 남습니다.
2. result API도 `scenePlan` 링크를 같이 내려주므로, 이후 web 쪽에서 실제 생성 결과를 읽어올 수 있는 기반이 생겼습니다.
3. artifact를 직접 보니, 현재 생성 품질 문제의 핵심이 더 분명해졌습니다.
   - renderer만의 문제가 아니라
   - deterministic copy planning이 여전히 길고 둔하며
   - `secondaryText`와 `kicker`가 장면 역할에 맞게 정리되지 않고 있습니다.

### artifact

- `docs/experiments/artifacts/exp-14-worker-scene-plan-bridge/promotion-scene-plan.json`
- `docs/experiments/artifacts/exp-14-worker-scene-plan-bridge/review-scene-plan.json`
- `docs/experiments/artifacts/exp-14-worker-scene-plan-bridge/summary.json`

## 6. 실패/제약

1. bridge는 생겼지만, scene plan에 들어가는 copy 자체는 아직 deterministic baseline 품질을 그대로 반영합니다.
2. 즉, 지금부터는 다시 `copy planning / prompt lever / model benchmark` 쪽을 재개해야 합니다.
3. scene plan을 web surface에 바로 소비하도록 연결한 것은 아직 아닙니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - renderer spike를 실제 생성 경로와 다시 연결하는 데 성공했습니다.
  - 이제는 더 이상 순수 UI polish가 아니라, scene plan에 들어갈 실제 문구 품질을 개선하는 생성 실험으로 돌아가야 합니다.

## 8. 다음 액션

1. `T02` 또는 `T04` 기준으로 실제 `copy planning` 개선 실험을 재개합니다.
2. 그 위에서 `Gemma 4` 포함 prompt/model 실험을 다시 붙입니다.
3. 이후 web/capture가 hardcoded data 대신 `scene-plan.json`을 읽도록 연결합니다.

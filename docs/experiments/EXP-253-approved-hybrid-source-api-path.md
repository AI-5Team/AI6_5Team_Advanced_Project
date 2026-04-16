# EXP-253 Approved Hybrid Source API Path

## 1. 기본 정보

- 실험 ID: `EXP-253`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `승격된 manual-review hybrid source 후보를 API generate 경로에서 직접 재사용`

## 2. 왜 이 작업을 했는가

- `EXP-252`까지는 `promoted_manual_review` 후보가 spike selection 경로로 다시 들어오는 것만 검증됐습니다.
- 하지만 서비스 본선에서는 `/api/projects/{project_id}/generate` 요청에서 approved candidate를 바로 태울 수 있어야 실제 baseline으로 쓸 수 있습니다.
- 이번 작업의 목적은 `decision log -> approved candidate key -> API input snapshot -> worker hybrid render`가 하나의 경로로 실제 동작하는지 확인하는 것입니다.

## 3. 구현 요약

1. `services/api/app/schemas/api.py`에 `approvedHybridSourceCandidateKey`를 추가해 generate/regenerate 요청이 approved candidate key를 공식적으로 받을 수 있게 했습니다.
2. `services/api/app/api/routes.py`는 `GenerateRequest`, `RegenerateRequest`를 실제 라우트 바디 스키마로 사용하도록 정리했습니다.
3. `services/api/app/core/config.py`에 `APP_MANUAL_REVIEW_DECISIONS_DIR` 설정을 추가했습니다.
4. `services/api/app/services/runtime.py`는 approved candidate key가 들어오면 decision artifact에서 `promote` 상태를 확인하고, source video를 프로젝트 storage로 stage한 뒤 `input_snapshot.hybridSourceVideoPath`, `input_snapshot.hybridSourceSelection`을 채우도록 확장했습니다.
5. result API의 `rendererSummary`에는 `hybridSourceSelectionMode`, `hybridSourceCandidateKey`도 함께 노출되도록 했습니다.

## 4. 실행

### 4.1 코드 검증

```bash
python -m py_compile services/api/app/core/config.py services/api/app/schemas/api.py services/api/app/api/routes.py services/api/app/services/runtime.py services/api/tests/test_api_smoke.py
uv run --project services/worker pytest services/api/tests/test_api_smoke.py -q
```

### 4.2 artifact 생성 smoke

- artifact root: `docs/experiments/artifacts/exp-253-approved-hybrid-source-api-path`
- 내부에 아래를 함께 남겼습니다.
  - promoted decision artifact
  - approved source mp4
  - API runtime storage
  - 최종 summary artifact

## 5. 결과

artifact summary: `docs/experiments/artifacts/exp-253-approved-hybrid-source-api-path/summary.json`

- `status=generated`
- `templateId=T02`
- `inputSnapshot.approvedHybridSourceCandidateKey=EXP-253-approved-hybrid-source-api-path::테스트라떼::approved_demo`
- `inputSnapshot.hybridSourceSelection.selectionMode=promoted_manual_review`
- `rendererSummary.videoSourceMode=hybrid_generated_clip`
- `rendererSummary.motionMode=hybrid_overlay_packaging`
- `rendererSummary.framingMode=hybrid_source_video`
- `rendererSummary.durationStrategy=freeze_last_frame`
- `rendererSummary.targetDurationSec=6.4`
- `rendererSummary.hybridSourceSelectionMode=promoted_manual_review`

test 결과:

- `services/api/tests/test_api_smoke.py`: `6 passed`

## 6. 해석

1. 이제 `approvedHybridSourceCandidateKey` 하나만 넘기면, API generate 경로가 approved decision을 읽어 source mp4를 project storage로 옮기고 worker hybrid renderer를 직접 사용합니다.
2. 즉 `EXP-252`까지 닫힌 spike 경로가 실제 서비스 API 입력 경로에도 연결됐습니다.
3. renderer summary에 provenance가 함께 노출되므로 결과 화면이나 운영 확인 시 `scene_image_render`와 `approved hybrid source`를 구분할 수 있습니다.

## 7. 결론

- `promoted manual-review candidate`는 이제 spike 전용 후보가 아니라 API generate baseline에서도 재사용 가능한 입력 단위가 됐습니다.
- 따라서 다음부터는 lane별로 `approved candidate`를 더 쌓는 것이 의미가 있으며, 새로운 임시 분기보다 `decision -> registry -> API input` 체계 안에서 누적하는 편이 맞습니다.

## 8. 다음 액션

1. 실제 `맥주 / accept`, `규카츠 / promoted manual_review`처럼 lane별 approved candidate inventory를 명시적으로 정리합니다.
2. web generate 진입점에서도 approved candidate 선택 또는 추천 정보를 노출할지 판단합니다.
3. 이후 실험은 `아무 source든 생성`보다 `approved candidate를 얼마나 안정적으로 늘릴 수 있는가`에 초점을 맞춥니다.

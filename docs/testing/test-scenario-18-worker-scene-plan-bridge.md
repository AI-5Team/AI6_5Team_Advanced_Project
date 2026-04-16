# 테스트 시나리오 18 - Worker Scene Plan Bridge 검증

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-18`

## 2. 테스트 목적

- worker generation path가 `scene-plan.json`을 실제로 생성하는지 검증합니다.
- result API가 `scenePlan` 링크를 함께 내려주는지 확인합니다.

## 3. 사전 조건

- `services/worker` 및 `services/api` 테스트 실행 가능 상태
- sample 이미지 사용 가능 상태

## 4. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_generation_pipeline.py`
2. `uv run --project services/api pytest services/api/tests/test_api_smoke.py`
3. `uv run --project services/worker python scripts/export_scene_plan_samples.py`
4. artifact JSON 확인

## 5. 결과

- worker tests: 통과
- api tests: 통과
- export script: 통과
- 생성 artifact:
  - `promotion-scene-plan.json`
  - `review-scene-plan.json`
  - `summary.json`

## 6. 관찰 내용

1. generation run 결과물에 `scene-plan.json`이 포함됩니다.
2. `/api/projects/{projectId}/result` 응답에 `scenePlan` 링크가 포함됩니다.
3. artifact를 통해 현재 생성 경로의 copy 품질 문제가 renderer만의 문제가 아니라는 점을 확인할 수 있습니다.

## 7. 실패/제약

1. scene plan bridge가 생겨도 copy 품질이 자동으로 좋아지지는 않습니다.
2. 현재 scene plan은 web에서 바로 소비하지 않고, artifact 및 API 링크 수준까지만 연결됐습니다.

## 8. 개선 포인트

1. 다음은 `T02/T04` 기준 copy planning 개선 실험입니다.
2. 그 다음 hardcoded scene 대신 `scenePlan` 기반 web 연결을 검토합니다.

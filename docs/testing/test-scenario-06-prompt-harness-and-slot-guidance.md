# 테스트 시나리오 06 - Prompt Harness 기준선 및 Slot Guidance 검증

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-06`

## 2. 테스트 목적

- prompt experiment harness가 production deterministic 경로를 깨뜨리지 않는지 확인합니다.
- `Gemma 4` 기반 prompt 실험이 실제로 실행되고 artifact를 남기는지 확인합니다.
- baseline 조건이 고정된 상태에서 slot guidance 레버 1개만 바뀌는지 확인합니다.

## 3. 사전 조건

- `GEMINI_API_KEY` 환경 변수가 설정돼 있어야 합니다.
- `uv`, `ffmpeg`, `npm`이 로컬에서 실행 가능해야 합니다.
- 샘플 자산은 `scripts/generate_sample_assets.py`로 생성합니다.

## 4. 수행 항목

1. `npm run worker:test`
2. `uv run --project services/worker python scripts/generate_sample_assets.py`
3. `uv run --project services/worker python scripts/run_prompt_experiment.py --experiment-id EXP-01`
4. `npm run check`

## 5. 결과

- `worker:test`: 통과
- 샘플 자산 생성: 통과
- `EXP-01` prompt 실험 실행: 통과
- 전체 `npm run check`: 통과
- artifact 경로:
  - `docs/experiments/artifacts/exp-01-slot-guidance-gemma4.json`

## 6. 관찰 내용

- production deterministic 경로 테스트는 그대로 통과했습니다.
- prompt harness는 별도 경로에서 동작해 production generation 로직을 대체하지 않았습니다.
- 첫 모델 응답에서 JSON 전처리 보강이 필요했고, 보강 후 정상 artifact를 저장했습니다.
- baseline prompt와 explicit slot guidance prompt는 동일 모델/동일 입력 조건에서 실행됐습니다.

## 7. 실패/제약

1. `scripts/run_prompt_experiment.py` 초기 실행 시 Python path 보정이 필요했습니다.
2. 샘플 자산이 없는 상태에서는 실험이 바로 실행되지 않았습니다.
3. Gemma 4 응답 시간이 약 52~60초로 짧지는 않았습니다.

## 8. 개선 포인트

1. prompt experiment 실행 전 샘플 자산 존재 여부를 자동 확인하는 preflight를 추가할 수 있습니다.
2. JSON schema 강제 수준을 높여 모델의 사전 설명 텍스트를 더 줄일 필요가 있습니다.
3. 사람이 읽는 비교 리포트를 자동 생성하도록 harness 출력 형식을 확장할 수 있습니다.

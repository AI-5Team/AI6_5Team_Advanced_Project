# 테스트 시나리오 32 - Gemini Flash Strict JSON Output Constraint

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-32`

## 2. 테스트 목적

- `Gemini 2.5 Flash`에서 strict JSON output constraint 한 레버가 format failure를 줄이는지 확인합니다.

## 3. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py`
2. `uv run --project services/worker python scripts/run_prompt_experiment.py --experiment-id EXP-28`

## 4. 결과

- pytest: 통과
- `EXP-28`: 실행 완료
- 생성 artifact:
  - `exp-28-gemini-2-5-flash-prompt-lever-experiment-strict-json-output-constraint.json`

## 5. 관찰 내용

1. baseline과 variant 모두 `invalid JSON response`로 실패했습니다.
2. prompt-level strict JSON constraint만으로는 이 모델의 형식 실패가 해결되지 않았습니다.

## 6. 실패/제약

1. 품질 비교까지 가지 못했습니다.
2. 단일 실행 1회입니다.

## 7. 개선 포인트

1. 이 모델은 prompt 레버보다 응답 길이/자산 수/토큰 설정을 먼저 줄여 볼 필요가 있습니다.
2. 당장 다음 우선순위는 Hugging Face 기반 오픈소스 비교 경로입니다.

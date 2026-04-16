# 테스트 시나리오 27 - Cross-Provider Model Comparison Harness

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-27`

## 2. 테스트 목적

- provider가 다른 모델을 같은 고정 prompt로 비교할 수 있는지 확인합니다.
- 실패 모델도 실험 artifact에 남는지 검증합니다.

## 3. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py`
2. `uv run --project services/worker python scripts/run_model_comparison_experiment.py --experiment-id EXP-23`

## 4. 결과

- pytest: 통과
- `EXP-23`: 실행 완료
- 생성 artifact:
  - `exp-23-service-aligned-promotion-cross-provider-model-comparison.json`

## 5. 관찰 내용

1. `Gemma 4` 결과는 정상 저장됩니다.
2. `OpenAI` 두 모델은 key invalid 상태여도 artifact에 실패 사유가 남습니다.
3. 에러 메시지는 key 일부가 남지 않도록 마스킹됩니다.

## 6. 실패/제약

1. 현재 `OPENAI_API_KEY`가 유효하지 않아 실제 품질 비교는 불가능합니다.
2. 따라서 이번 테스트는 cross-provider harness 동작 검증에 더 가깝습니다.

## 7. 개선 포인트

1. key 정상화 후 `EXP-23` 재실행이 필요합니다.
2. 그 전까지는 실행 가능한 provider/model family 비교를 우선 진행합니다.

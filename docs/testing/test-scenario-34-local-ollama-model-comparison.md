# 테스트 시나리오 34 - Local Ollama Model Comparison

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-34`

## 2. 테스트 목적

- `RTX 4080 Super 16GB / RAM 64GB` 환경에서 이미 설치된 로컬 `Ollama` 모델이 현재 copy generation harness에서 실제로 동작하는지 확인합니다.

## 3. 수행 항목

1. `nvidia-smi`
2. `ollama list`
3. `ollama show gemma3:12b`
4. `ollama show exaone3.5:7.8b`
5. `ollama show mistral-small3.1:24b-instruct-2503-q4_K_M`
6. `ollama show llama3.1:8b`
7. `uv run --project services/worker pytest services/worker/tests/test_env_loader.py services/worker/tests/test_prompt_harness.py`
8. `uv run --project services/worker python scripts/run_model_comparison_experiment.py --experiment-id EXP-30`

## 4. 결과

- local GPU 확인: 통과
- installed Ollama models 확인: 통과
- pytest: 통과
- `EXP-30`: 실행 완료
- 생성 artifact:
  - `exp-30-local-ollama-model-comparison-on-4080-super.json`

## 5. 관찰 내용

1. `gemma3:12b`, `mistral-small3.1:24b-instruct-2503-q4_K_M`는 vision capability가 확인됐습니다.
2. `exaone3.5:7.8b`는 한국어 자연스러움이 좋았고, 한글 깨짐 heuristic에도 걸리지 않았습니다.
3. `llama3.1:8b`는 schema 안정성이 부족했습니다.
4. 이번 샘플에서는 로컬 모델 4종 모두 명백한 한글 mojibake는 보이지 않았습니다.

## 6. 실패/제약

1. text-only 모델과 vision 모델을 같은 표에서 비교했습니다.
2. `mistral-small3.1:24b`는 응답 시간이 길었습니다.

## 7. 개선 포인트

1. `EXAONE 3.5 7.8B`와 `Gemma3 12B`를 우선 후보로 계속 봅니다.
2. 다음은 로컬 후보 중 하나를 고정하고 prompt lever 실험으로 이어갑니다.

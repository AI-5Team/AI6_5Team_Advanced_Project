# 테스트 시나리오 33 - Hugging Face Open-Source Model Comparison

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-33`

## 2. 테스트 목적

- `HF_TOKEN`을 실제로 사용해 Hugging Face router 기반 오픈소스 모델 비교 경로가 동작하는지 확인합니다.

## 3. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py`
2. `uv run --project services/worker python scripts/run_model_comparison_experiment.py --experiment-id EXP-29`

## 4. 결과

- pytest: 통과
- `EXP-29`: 실행 완료
- 생성 artifact:
  - `exp-29-hugging-face-open-source-text-model-comparison.json`

## 5. 관찰 내용

1. `Qwen/Qwen3-4B-Instruct-2507`는 실제로 응답했습니다.
2. `Qwen/Qwen3.5-27B`는 provider timeout으로 실패했습니다.
3. Hugging Face 경로는 열렸지만, provider 접근성 차이까지 같이 봐야 합니다.

## 6. 실패/제약

1. 이번 경로는 text-only입니다.
2. multimodal 비교는 아직 아닙니다.

## 7. 개선 포인트

1. `Qwen/Qwen3-4B-Instruct-2507`를 대상으로 constraint 실험을 이어갑니다.
2. 실제로 통과하는 다른 오픈소스 후보를 더 찾습니다.

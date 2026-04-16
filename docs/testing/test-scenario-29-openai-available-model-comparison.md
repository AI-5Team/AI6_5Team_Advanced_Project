# 테스트 시나리오 29 - OpenAI Available Model Comparison

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-29`

## 2. 테스트 목적

- 현재 계정에서 실제 사용 가능한 OpenAI 모델(`gpt-5-mini`, `gpt-5-nano`)과 `Gemma 4`를 동일 조건으로 비교합니다.
- `.env.local`에 넣은 새 OpenAI key가 worker harness에서 정상 반영되는지도 같이 확인합니다.

## 3. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_env_loader.py services/worker/tests/test_prompt_harness.py`
2. `uv run --project services/worker python scripts/run_model_comparison_experiment.py --experiment-id EXP-25`

## 4. 결과

- pytest: 통과
- `EXP-25`: 실행 완료
- 생성 artifact:
  - `exp-25-service-aligned-promotion-openai-available-model-comparison.json`

## 5. 관찰 내용

1. `Gemma 4`와 `gpt-5-mini`는 모두 실패 체크 없이 실행됐습니다.
2. `gpt-5-mini`는 `s2`만 길이 초과라서 실전 후보로 남길 수 있습니다.
3. `gpt-5-nano`는 모든 scene가 길이 초과라 render-ready 기준에서는 불리했습니다.
4. 첫 시도에서 OpenAI는 `temperature` 미지원으로 실패했고, 파라미터를 줄인 뒤 정상 실행됐습니다.

## 6. 실패/제약

1. 단일 실행 1회입니다.
2. 현재 평가는 scene-plan/text budget heuristic 중심이라 실제 체감 품질과 완전히 같다고 보긴 어렵습니다.
3. Hugging Face token은 이번 테스트에서 아직 직접 사용하지 않았습니다.

## 7. 개선 포인트

1. `T04 review`에서도 같은 모델 비교를 이어갑니다.
2. `gpt-5-mini`는 길이 제약을 한 레버로 더 조여 봅니다.
3. 오픈소스 비교는 Hugging Face 경로를 별도 추가합니다.

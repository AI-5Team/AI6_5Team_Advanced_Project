# 테스트 시나리오 37 - Local EXAONE Output Constraint

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-37`

## 2. 테스트 목적

- 로컬 `EXAONE 3.5 7.8B`에서 `output_constraint` 한 레버가 `T02 promotion`의 길이/CTA/형식 안정성을 개선하는지 확인합니다.

## 3. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py`
2. `uv run --project services/worker python scripts/run_prompt_experiment.py --experiment-id EXP-33 --api-key-env OLLAMA_HOST`

## 4. 결과

- pytest: 통과
- `EXP-33`: 실행 완료
- 생성 artifact:
  - `exp-33-local-exaone-3-5-7-8b-prompt-lever-experiment-promotion-output-constraint.json`

## 5. 관찰 내용

1. output constraint를 붙인 variant는 hashtags 개수를 5개로 맞췄습니다.
2. CTA도 더 짧고 직접적으로 정리됐습니다.
3. 하지만 region repeat는 줄지 않았습니다.

## 6. 실패/제약

1. 이번 실험은 완전 성공이 아니라 부분 성공입니다.
2. format/readability는 개선됐지만 핵심 policy failure는 남았습니다.

## 7. 개선 포인트

1. 다음 레버는 `caption region budget` 또는 `hashtag rule`이 더 적절합니다.
2. 같은 output constraint를 `Gemma3 12B`에도 붙여 비교해 볼 가치가 있습니다.

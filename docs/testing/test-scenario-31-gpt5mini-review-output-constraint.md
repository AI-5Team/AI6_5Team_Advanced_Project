# 테스트 시나리오 31 - GPT-5 Mini Review Output Constraint

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-31`

## 2. 테스트 목적

- `gpt-5-mini`를 고정하고 `review(T04)`에서 output constraint 한 레버가 실제로 render-readiness를 개선하는지 확인합니다.

## 3. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py`
2. `uv run --project services/worker python scripts/run_prompt_experiment.py --experiment-id EXP-27 --api-key-env OPENAI_API_KEY`

## 4. 결과

- pytest: 통과
- `EXP-27`: 실행 완료
- 생성 artifact:
  - `exp-27-gpt-5-mini-prompt-lever-experiment-review-output-constraint.json`

## 5. 관찰 내용

1. baseline은 `ctaText lacks explicit action keyword`로 실패했습니다.
2. output constraint variant는 실패 체크가 없어졌고, scene 길이 초과도 사라졌습니다.
3. `gpt-5-mini`는 review 템플릿에서 prompt constraint에 잘 반응했습니다.

## 6. 실패/제약

1. CTA 문구가 충분히 공격적인지는 별도 검토가 필요합니다.
2. 단일 실행 1회입니다.

## 7. 개선 포인트

1. 같은 방식으로 `promotion`에도 적용 가능한지 추후 확인합니다.
2. 다음은 `Gemini 2.5 Flash` format 안정화 실험으로 이어갑니다.

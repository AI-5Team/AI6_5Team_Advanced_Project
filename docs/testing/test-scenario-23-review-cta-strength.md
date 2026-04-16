# 테스트 시나리오 23 - Review CTA Strength

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-23`

## 2. 테스트 목적

- `EXP-19`가 `T04 review`에서 CTA 행동성만 더 직접적으로 바꾸는지 확인합니다.
- CTA 강도 지시가 실제 `ctaText`, closing scene CTA를 더 직접적으로 만드는지 검증합니다.

## 3. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py`
2. `uv run --project services/worker python scripts/run_prompt_experiment.py --experiment-id EXP-19`
3. artifact JSON 확인

## 4. 결과

- prompt harness tests: 통과
- `EXP-19` 실행: 통과
- artifact:
  - `docs/experiments/artifacts/exp-19-gemma-4-prompt-lever-experiment-review-cta-strength.json`

## 5. 관찰 내용

1. CTA strength variant는 `지금 바로 달려가기`보다 `지금 저장하기`처럼 더 직접적인 행동 문구를 만들었습니다.
2. region repeat는 baseline과 같은 수준으로 유지했습니다.
3. `review` 템플릿에서도 CTA 강도가 강한 레버로 보입니다.

## 6. 실패/제약

1. 1차 실행에서 `저장`이 CTA action keyword에 빠져 있어 평가 규칙 수정 후 재실행했습니다.
2. 단일 실행 1회입니다.

## 7. 개선 포인트

1. 다음은 `promotion`과 `review`의 상위 레버를 비교 표로 정리합니다.
2. 이후 `scenePlan` 기반 web 연결로 넘어갑니다.

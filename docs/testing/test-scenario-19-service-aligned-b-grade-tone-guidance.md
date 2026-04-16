# 테스트 시나리오 19 - Service-Aligned B-Grade Tone Guidance

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-19`

## 2. 테스트 목적

- `EXP-15` prompt harness가 `T02`의 실제 슬롯 구조(`hook`, `benefit`, `urgency`, `cta`)를 올바르게 요구하는지 확인합니다.
- `scene-plan` 기준으로 Gemma 4 baseline prompt와 `B급 tone guidance` variant 차이를 검증합니다.

## 3. 사전 조건

- `GEMINI_API_KEY` 설정
- `docs/sample` 실제 음식 사진 존재
- `services/worker` 테스트 실행 가능 상태

## 4. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py`
2. `uv run --project services/worker python scripts/run_prompt_experiment.py --experiment-id EXP-15`
3. artifact JSON 확인

## 5. 결과

- prompt harness tests: 통과
- `EXP-15` 실행: 통과
- artifact:
  - `docs/experiments/artifacts/exp-15-gemma-4-prompt-lever-experiment-service-aligned-b-grade-tone.json`

## 6. 관찰 내용

1. prompt JSON shape가 템플릿의 실제 `textRole`을 동적으로 반영합니다.
2. `B급 tone guidance` variant는 `failed_checks` 없이 통과했습니다.
3. deterministic baseline은 `b_grade_fun` 길이 예산을 여전히 초과합니다.
4. Gemma 결과는 `scene-plan` 기준으로 over-limit scene을 제거했습니다.

## 7. 실패/제약

1. 1차 실행에서는 prompt harness shape가 `T02` 슬롯을 제대로 반영하지 못해 재실행이 필요했습니다.
2. CTA heuristic에 `예약`이 빠져 있어 평가 규칙도 함께 수정해야 했습니다.
3. 단일 실행 1회라 재현성은 부족합니다.

## 8. 개선 포인트

1. 다음은 `T04 review` 시나리오로 확장합니다.
2. 다음 레버는 `CTA 강도`로 고정합니다.
3. 이후 web이 `scenePlan`을 직접 소비하도록 연결합니다.

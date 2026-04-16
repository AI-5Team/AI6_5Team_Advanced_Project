# 테스트 시나리오 21 - Review Slot Length Cap

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-21`

## 2. 테스트 목적

- `EXP-17`이 `T04 review`의 slot 길이 제약을 prompt에 정확히 반영하는지 확인합니다.
- 길이 제약이 실제 `scene-plan` 과긴 문구를 줄이는지 검증합니다.

## 3. 수행 항목

1. `uv run --project services/worker pytest services/worker/tests/test_prompt_harness.py`
2. `uv run --project services/worker python scripts/run_prompt_experiment.py --experiment-id EXP-17`
3. artifact JSON 확인

## 4. 결과

- prompt harness tests: 통과
- `EXP-17` 실행: 통과
- artifact:
  - `docs/experiments/artifacts/exp-17-gemma-4-prompt-lever-experiment-review-slot-length-cap.json`

## 5. 관찰 내용

1. slot 길이 제약 variant는 `over-limit scene`을 `1 -> 0`으로 줄였습니다.
2. 하지만 지역 반복과 CTA 표현 쪽은 오히려 나빠졌습니다.
3. 따라서 `길이 제약`은 유효하지만 단독 승리 레버는 아니었습니다.

## 6. 실패/제약

1. 단일 실행 1회입니다.
2. CTA heuristic은 colloquial B급 표현을 보수적으로 평가합니다.

## 7. 개선 포인트

1. 다음은 `지역 반복 제약`을 한 레버로 봅니다.
2. 이후 `CTA 강도` 실험을 이어갑니다.

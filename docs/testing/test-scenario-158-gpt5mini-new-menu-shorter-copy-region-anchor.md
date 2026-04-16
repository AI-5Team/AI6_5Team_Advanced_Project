# Test Scenario 158

## 목적

- `EXP-156`의 실행 경로가 실제 응답을 받는지 확인합니다.

## 실행

- `python scripts/run_prompt_experiment.py --experiment-id EXP-156`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-156 --repeat 3`

## 기대 결과

- baseline 또는 candidate가 최소 1회 이상 정상 응답을 반환해야 합니다.

## 실제 결과

- 초기 상태:
  - process env key direct call `401 invalid_api_key`
  - repo `.env.local` key direct call `200`
  - 원인: runner 기본 `--api-key-env=GEMINI_API_KEY`
- 수정 후:
  - baseline `3/3`, `avg_score=100.0`
  - candidate `3/3`, `avg_score=100.0`

## 판정

- 통과
- 참고: credential 자체보다 runner 기본 env 선택 버그가 원인이었습니다.

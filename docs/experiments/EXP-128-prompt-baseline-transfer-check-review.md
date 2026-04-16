# EXP-128 Prompt Baseline Transfer Check Review

## 목적

- `T02 promotion`에서 고정한 strict baseline 원칙이 `T04 review`까지 실제로 전이되는지 확인합니다.
- `직접 이식`과 `review slot 번역` 두 방식을 나눠 봐서, baseline이 어떤 수준까지 재사용 가능한지 확인합니다.

## 변경 범위

- `services/worker/experiments/prompt_harness.py`
  - `EXP-128`을 추가했습니다.
  - `promotion_baseline_direct_transfer_to_review`
  - `promotion_baseline_principles_translated_to_review`
- `scripts/run_prompt_variant_repeatability_spot_check.py`
  - 고정 모델 아래에서 prompt variant repeatability를 다시 돌릴 수 있는 runner를 추가했습니다.

## 비교한 variant

- direct transfer
  - `T02 promotion` strict baseline의 핵심 제약을 거의 그대로 `T04 review`에 옮긴 variant입니다.
  - 예상은 `review slot`과 안 맞아 무너질 가능성이었습니다.
- translated transfer
  - strict anchor, exact region, CTA action성 같은 baseline 원칙은 유지하되 `review_quote / product_name / cta` 구조에 맞춰 다시 번역한 variant입니다.

## single run 결과

artifact:

- `docs/experiments/artifacts/exp-128-prompt-baseline-transfer-check-t02-promotion-to-t04-review.json`

주요 결과:

- deterministic reference
  - `score=93.3`
  - 실패: `region repeated more than allowed`
  - over-limit scene: `s1`, `s2`
- direct transfer
  - `score=100.0`
  - 실패 없음
  - hook: `한 번 먹고 기억나요`
  - cta: `저장하고 방문하기`
- translated transfer
  - `score=100.0`
  - 실패 없음
  - hook: `한 입 먹고 바로 기절함`
  - cta: `저장하고 방문하기`

## repeatability 결과

artifact:

- `docs/experiments/artifacts/exp-128-variant-repeatability.json`

주요 결과:

- direct transfer
  - `run_count=3`
  - `success_count=1`
  - `avg_score=33.3`
  - 성공 1회는 `score=100.0`
  - 실패 2회는 모두 `The read operation timed out`
- translated transfer
  - `run_count=3`
  - `success_count=1`
  - `avg_score=33.3`
  - 성공 1회는 `score=100.0`
  - 실패 2회는 모두 `The read operation timed out`

## 해석

- 이번 결과는 `prompt quality collapse`가 아니라 `provider/runtime timeout instability`가 더 크게 드러난 케이스입니다.
- 요청이 정상 완료된 run에서는 direct transfer와 translated transfer 모두 `100.0`을 통과했습니다.
- 따라서 `T02 promotion baseline`의 핵심 원칙은 `T04 review`까지도 전이 가능하다는 신호가 분명히 있습니다.
- 다만 이 결과만으로 `T04 review baseline`을 안정적으로 freeze했다고 보기는 어렵습니다.
- 이유는 repeatability 실패 원인이 품질 저하가 아니라 API timeout이었고, 운영 baseline 관점에서는 이 역시 실제 리스크이기 때문입니다.

## 판단

- `baseline principle transfer` 자체는 유효합니다.
- 하지만 `T04 review`를 독립 baseline으로 고정하려면 품질뿐 아니라 운영 안정성까지 같이 봐야 합니다.
- 따라서 다음 단계는 `Gemma 4 timeout이 있을 때 review baseline을 누가 fallback할 수 있는지` 확인하는 쪽이 맞습니다.

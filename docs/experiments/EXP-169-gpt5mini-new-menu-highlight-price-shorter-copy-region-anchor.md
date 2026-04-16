# EXP-169 GPT-5 Mini New Menu Highlight Price Shorter Copy Region Anchor

## 배경

- `EXP-168` 기준 최상위 `P2` 후보 중 하나는 `T01 new_menu / friendly / highlightPrice=true / shorterCopy=true / emphasizeRegion=true`였습니다.
- 가장 가까운 기존 profile은 `new_menu_friendly_region_anchor_shorter_copy`였고, 이 조합은 `highlightPrice=true`만 추가 해석하면 되는 상태였습니다.
- 따라서 새 축을 크게 여는 대신, 기존 shorter-copy profile 위에 `숫자 가격 환각 없는 value emphasis`만 결합하는 접근이 가장 자연스러웠습니다.

## 목표

- `highlightPrice=true`와 `shorterCopy=true`를 함께 걸어도 짧은 문장 구조를 유지하면서, 가격 숫자 환각 없이 가치 포인트를 더 먼저 보이게 만들 수 있는지 확인합니다.
- `gpt-5-mini`를 고정한 채 baseline 재사용과 candidate variant를 비교해 combined option profile 승격 가능 여부를 판단합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-cafe-new-menu-fixed-highlight-price-shorter-copy`
- 추가 experiment:
  - `EXP-169`
- variant:
  - baseline: `new_menu_friendly_region_anchor_shorter_copy_baseline_highlight_price_gpt5mini`
  - candidate: `new_menu_friendly_region_anchor_highlight_price_shorter_copy_gpt5mini`

## 실행

- `python -m py_compile services/worker/experiments/prompt_harness.py`
- `python scripts/run_prompt_experiment.py --experiment-id EXP-169`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-169 --repeat 3`

artifact:

- `docs/experiments/artifacts/exp-169-gpt-5-mini-new-menu-highlight-price-shorter-copy-region-anchor.json`
- `docs/experiments/artifacts/exp-169-variant-repeatability.json`

## 결과

### single run

| variant | score | hook | difference | cta |
|---|---:|---|---|---|
| deterministic reference | `93.3` | `성수동에서 먼저 만나는 신메뉴` | `가격 포인트가 먼저 보이도록 구성했습니다` | `오늘 바로 방문해 보세요` |
| baseline | `100.0` | `성수동에서 이거 보셨나요?` | `부드러운 생크림+과즙` | `방문해서 확인` |
| candidate | `100.0` | `성수동에서 이거 보셨나요?` | `부드러운 크림과 생딸기 조합` | `방문해보세요` |

### repeatability

| variant | success | avg score | avg hook length | avg cta length |
|---|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `14.0` | `5.7` |
| candidate | `3/3` | `100.0` | `12.3` | `5.7` |

## 해석

1. baseline/candidate 모두 품질선은 통과했습니다.
2. candidate는 shorter-copy 구조를 유지하면서 hook 길이를 더 짧게 만들었고, `difference/subText`를 한 줄 가치 포인트로 압축했습니다.
3. 숫자 가격, 할인율, 세일 문구를 새로 만들지 않았고, `highlightPrice=true`를 `짧은 가치 포인트 강조`로 해석하는 데 성공했습니다.

## 판단

- `EXP-169`는 `new_menu highlightPrice=true + shorterCopy=true` combined option profile 승격 근거로 사용할 수 있습니다.
- 이 결과로 `new_menu` 비지역 `P2`는 모두 정리됐고, 남은 최상위 `P2`는 `review` 2건입니다.

# EXP-189 GPT-5 Mini New Menu Shorter Copy Minimal Region Anchor

## 배경

- `EXP-188` 기준 최상위 `P2` 하나는 `T01 new_menu / friendly / highlightPrice=false / shorterCopy=true / emphasizeRegion=false`였습니다.
- baseline은 이미 `new_menu_friendly_minimal_region_anchor`로 정리됐으므로, 이번에는 같은 minimal anchor 위에 `shorterCopy=true`만 더하면 되는 상태였습니다.

## 목표

- minimal region anchor를 유지한 채 `shorterCopy=true`를 한 포인트 압축 규칙으로 안정적으로 추가할 수 있는지 확인합니다.

## 실행

- `python -m py_compile services/worker/experiments/prompt_harness.py`
- `python scripts/run_prompt_experiment.py --experiment-id EXP-189`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-189 --repeat 3`

artifact:

- `docs/experiments/artifacts/exp-189-gpt-5-mini-new-menu-shorter-copy-minimal-region-anchor.json`
- `docs/experiments/artifacts/exp-189-variant-repeatability.json`

## 결과

### single run

| variant | score | hook | cta |
|---|---:|---|---|
| baseline | `100.0` | `생크림 가득한 딸기라떼?` | `저장하고 확인` |
| candidate | `100.0` | `딸기 크림 라떼, 어때요?` | `저장하고확인` |

### repeatability

| variant | success | avg score | avg hook length | avg cta length |
|---|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `11.0` | `7.0` |
| candidate | `3/3` | `100.0` | `10.0` | `6.3` |

## 해석

1. candidate는 minimal region anchor를 유지하면서 hook/product/difference를 한 포인트씩 더 짧게 압축했습니다.
2. 지역 기준면은 줄이지 않고, 지역 외 surface만 짧게 만드는 쪽이 `shorterCopy=true` 해석에 더 일관됐습니다.

## 판단

- `EXP-189`는 `new_menu_friendly_minimal_region_anchor_shorter_copy` profile 승격 근거로 사용할 수 있습니다.


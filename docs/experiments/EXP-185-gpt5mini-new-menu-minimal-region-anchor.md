# EXP-185 GPT-5 Mini New Menu Minimal Region Anchor

## 배경

- `EXP-184` 기준 최상위 `P3` 중 가장 먼저 볼 축은 `T01 new_menu / friendly / highlightPrice=false / shorterCopy=false / emphasizeRegion=false`였습니다.
- `new_menu` copy-rule은 region slot 최소 2개를 요구하므로, 이 조합은 `무지역`이 아니라 `caption 1개 + #성수동 1개`만 남기는 minimal anchor로 해석하는 편이 맞았습니다.

## 목표

- `emphasizeRegion=false`에서도 detail-location leakage 없이 region anchor를 최소 surface로만 남길 수 있는지 확인합니다.
- hook의 지역명 foreground를 제거하면서도 option profile로 승격 가능한 안정성을 확보합니다.

## 실행

- `python -m py_compile services/worker/experiments/prompt_harness.py`
- `python scripts/run_prompt_experiment.py --experiment-id EXP-185`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-185 --repeat 3`

artifact:

- `docs/experiments/artifacts/exp-185-gpt-5-mini-new-menu-minimal-region-anchor.json`
- `docs/experiments/artifacts/exp-185-variant-repeatability.json`

## 결과

### single run

| variant | score | hook | cta |
|---|---:|---|---|
| deterministic reference | `93.3` | `성수동 기준 먼저 만나는 신메뉴로 분위기를 한 번에 보여드립니다` | `오늘 바로 방문해 보세요` |
| baseline | `100.0` | `성수동에서 이거 보셨나요?` | `방문 확인` |
| candidate | `100.0` | `새로운 달콤함, 궁금하지 않나요?` | `저장하고 확인` |

### repeatability

| variant | success | avg score | avg hook length | avg cta length |
|---|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `14.0` | `5.3` |
| candidate | `3/3` | `100.0` | `12.3` | `7.0` |

## 해석

1. candidate는 hook에서 지역명을 제거하고도 `caption 1개 + #성수동 1개`로 region 최소치를 안정적으로 유지했습니다.
2. 같은 세션 초안에서는 hashtag를 1개만 남겨 repeatability가 `93.3`으로 흔들렸고, 이후 `총 5~8개 hashtag 유지` 제약을 추가한 뒤 `3/3 pass`로 회복했습니다.
3. 따라서 `emphasizeRegion=false`는 `region 삭제`가 아니라 `region minimal anchor`로 정의하는 편이 현재 rule set과 더 잘 맞습니다.

## 판단

- `EXP-185`는 `new_menu_friendly_minimal_region_anchor` profile 승격 근거로 사용할 수 있습니다.


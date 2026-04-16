# EXP-156 GPT-5 Mini New Menu Shorter Copy Region Anchor

## 배경

- `EXP-155` 기준 최상위 `P2` 후보 중 하나는 `T01 new_menu / friendly / highlightPrice=false / shorterCopy=true / emphasizeRegion=true`였습니다.
- 가장 가까운 기존 profile은 `new_menu_friendly_strict_region_anchor`였고, mismatch 축은 `quickOptions.shorterCopy` 1개뿐이었습니다.
- 따라서 새 scenario를 따로 넓히기보다, 기존 `new_menu` strict region anchor prompt 위에 `shorterCopy=true` 압축 규칙만 더하는 접근이 가장 자연스러웠습니다.

## 목표

- `gpt-5-mini`를 고정한 채 `new_menu` strict region anchor baseline을 `shorterCopy=true` 조건으로 확장할 수 있는지 확인합니다.
- baseline 재사용과 candidate 압축 variant를 함께 비교해, manifest option profile 승격 가능 여부를 판단합니다.

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가 scenario:
  - `scenario-cafe-new-menu-fixed-shorter-copy`
- 추가 experiment:
  - `EXP-156`
- variant:
  - baseline: `new_menu_friendly_region_anchor_baseline_gpt5mini`
  - candidate: `new_menu_friendly_region_anchor_shorter_copy_gpt5mini`

## 실행

- `python -m py_compile services/worker/experiments/prompt_harness.py scripts/run_prompt_experiment.py scripts/run_prompt_variant_repeatability_spot_check.py scripts/run_prompt_baseline_snapshot.py`
- `python scripts/run_prompt_experiment.py --experiment-id EXP-156`
- `python scripts/run_prompt_variant_repeatability_spot_check.py --experiment-id EXP-156 --repeat 3`

artifact:

- `docs/experiments/artifacts/exp-156-gpt-5-mini-new-menu-shorter-copy-region-anchor.json`
- `docs/experiments/artifacts/exp-156-variant-repeatability.json`

## 결과

### 1차 실행에서 확인된 문제

| 항목 | 결과 |
|---|---:|---|
| process env `OPENAI_API_KEY` | OpenAI API 직접 호출 기준 `401 invalid_api_key` |
| repo `.env.local` `OPENAI_API_KEY` | OpenAI API 직접 호출 기준 `200` |
| 원인 | `run_prompt_experiment.py`, `run_prompt_variant_repeatability_spot_check.py` 기본 `--api-key-env`가 `GEMINI_API_KEY`였음 |

### 수정 후 single run

| variant | score | hook | cta |
|---|---:|---|---|
| deterministic reference | `93.3` | `성수동에서 먼저 만나는 신메뉴` | `오늘 바로 방문해 보세요` |
| baseline | `100.0` | `성수동에서 이거 보셨나요?` | `방문해 확인` |
| candidate | `100.0` | `성수동에서 이거 보셨나요?` | `방문해보기` |

### 수정 후 repeatability

| variant | success | avg score | avg hook length | avg cta length |
|---|---:|---:|---:|---:|
| baseline | `3/3` | `100.0` | `14.0` | `6.0` |
| candidate | `3/3` | `100.0` | `14.0` | `6.0` |

## 해석

1. 처음 보였던 401은 key 자체가 아니라 실험 스크립트 기본 env 선택 버그였습니다.
2. `prompt_harness`는 이미 `.env.local`을 로드하고 있었고, 문제는 CLI 기본 `--api-key-env`가 OpenAI 실험에서도 `GEMINI_API_KEY`였다는 점이었습니다.
3. 버그를 고친 뒤에는 baseline/candidate 모두 `3/3 all pass`를 기록했습니다.
4. 다만 manifest profile로는 baseline 재사용보다 `shorterCopy=true`를 명시한 candidate variant를 고정하는 편이 더 적절합니다.

## 판단

- `EXP-156`은 이제 `new_menu shorterCopy=true` option profile 승격 근거로 사용할 수 있습니다.
- 별도 profile은 `new_menu_friendly_region_anchor_shorter_copy`로 고정하고, prompt variant는 explicit shorter-copy candidate를 쓰는 편이 맞습니다.
- 같은 버그 재발을 막기 위해 CLI runner 기본 env 선택도 provider-specific으로 수정했습니다.

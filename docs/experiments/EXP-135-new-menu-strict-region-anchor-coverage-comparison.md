# EXP-135 New Menu Strict Region Anchor Coverage Comparison

## 배경

- `EXP-133`에서 `promptBaselineSummary`를 UI와 payload에 연결한 뒤, 현재 demo 기본 시나리오인 `T01 new_menu / friendly / emphasizeRegion=true`는 baseline coverage 밖으로 표시됐습니다.
- 현재 main baseline은 `T02 promotion / b_grade_fun / Gemma 4`이고, option profile은 `T04 review` fallback만 있었습니다.
- 이번 단계의 질문은 단순했습니다.
  1. `T02 strict baseline`의 핵심 원칙이 `T01 new_menu`에도 전이되는가
  2. 된다면 어떤 모델이 실제 coverage 후보가 되는가

## 목표

- `T01 new_menu / friendly / emphasizeRegion=true`에서 strict region anchor prompt를 고정하고 `Gemma 4`와 `gpt-5-mini`를 비교합니다.
- 특히 아래 2가지를 같이 봅니다.
  - `strict_all_surfaces` detail-location guard를 지키는가
  - single run이 아니라 repeatability까지 유지되는가

## 고정 조건

- scenario: `scenario-cafe-new-menu-fixed`
- template: `T01`
- style: `friendly`
- quick options:
  - `highlightPrice=false`
  - `shorterCopy=false`
  - `emphasizeRegion=true`
- model candidates:
  - `models/gemma-4-31b-it`
  - `gpt-5-mini`

## prompt 원칙

- `T02`에서 쓰던 strict baseline 구조를 `new_menu` slot에 맞게 번역했습니다.
- 핵심 제약:
  - `hook / product_name / difference` headline budget 고정
  - `cta`는 행동 단어로 시작
  - `emphasizeRegion=true`여도 `detailLocation`은 공개 금지
  - `서울숲`, `성수역`, `근처`, `인근` 등 nearby/detail-location 표현은 모든 surface에서 금지
  - `difference`는 위치 설명 대신 메뉴 특징/조합/맛만 남기기

## 구현

- 파일:
  - `services/worker/experiments/prompt_harness.py`
- 추가된 model comparison id:
  - `EXP-135`
- prompt variant id:
  - `fixed_new_menu_strict_region_anchor`

## 결과

artifact:
- `docs/experiments/artifacts/exp-135-new-menu-strict-region-anchor-coverage-comparison.json`
- `docs/experiments/artifacts/exp-135-repeatability.json`

### single run

| model | result | note |
|---|---:|---|
| deterministic reference | `93.3` | `region repeated more than allowed` |
| `Gemma 4` | `100.0` | hook: `성수동에서 이거 보셨나요?` |
| `gpt-5-mini` | `100.0` | hook: `성수동에서 이거 보셨나요?` |

### repeatability

| model | success | avg score | 해석 |
|---|---:|---:|---|
| `Gemma 4` | `0/3` | `0.0` | 3회 모두 `The read operation timed out` |
| `gpt-5-mini` | `3/3` | `100.0` | strict location policy와 scene budget 유지 |

`gpt-5-mini` sample hooks:
- `성수동에 이런 신메뉴가?`
- `성수동에서 이거 보셨나요?`

## 해석

1. `T02 strict baseline` 원칙 자체는 `T01 new_menu`로 전이 가능합니다.
2. deterministic reference는 여전히 `region repeat`에서 무너졌고, 이 coverage gap은 실제로 존재했습니다.
3. single run 기준 품질만 보면 `Gemma 4`와 `gpt-5-mini` 모두 통과했습니다.
4. 하지만 repeatability까지 보면 이번 조건의 실용 후보는 `gpt-5-mini`입니다.
5. `Gemma 4`는 품질 문제가 아니라 transport timeout으로 탈락했으므로, 이 결과는 prompt collapse가 아니라 운영성 이슈 재발로 보는 편이 맞습니다.

## 판단

- `T01 new_menu / friendly / emphasizeRegion=true`는 이제 coverage profile 후보로 올릴 수 있습니다.
- 다만 `main baseline`을 바꾸는 것이 아니라, `T01` 전용 조건부 profile로 관리하는 편이 맞습니다.
- 다음 단계는 이 결과를 manifest option profile로 승격하고 snapshot으로 재현 가능 상태를 만드는 것입니다.

## 관련 파일

- `services/worker/experiments/prompt_harness.py`
- `packages/template-spec/manifests/prompt-baseline-v1.json`

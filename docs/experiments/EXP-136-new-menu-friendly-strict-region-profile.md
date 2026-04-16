# EXP-136 New Menu Friendly Strict Region Profile

## 배경

- `EXP-135`에서 `T01 new_menu / friendly / emphasizeRegion=true` coverage를 따로 고정할 필요가 있다는 신호가 나왔습니다.
- single run은 `Gemma 4`, `gpt-5-mini` 모두 통과했지만 repeatability에서는 `gpt-5-mini`만 `3/3 pass`를 유지했습니다.
- 따라서 이번 단계는 `T01`을 main baseline으로 올리는 것이 아니라, `T01` 전용 candidate profile을 manifest 안에 등록하는 작업입니다.

## 목표

- `prompt-baseline-v1.json`에 `T01` coverage option profile을 추가합니다.
- 같은 profile을 `snapshot` runner로 다시 실행해 실제 acceptance를 확인합니다.

## 구현

### 1. manifest option profile 추가

- 파일: `packages/template-spec/manifests/prompt-baseline-v1.json`
- 추가 profile:
  - `new_menu_friendly_strict_region_anchor`
- 선택 모델:
  - `gpt-5-mini`
- source experiment:
  - `EXP-135`

### 2. manifest evidence 확장

- `transferChecks[]`에 `EXP-135` 결과를 추가했습니다.
- 요약:
  - single run은 `Gemma 4`, `gpt-5-mini` 모두 통과
  - repeatability는 `gpt-5-mini 3/3 pass`
  - `Gemma 4`는 3회 모두 transport timeout

### 3. README 반영

- 파일: `packages/template-spec/README.md`
- 현재 option profile 목록에 `new_menu_friendly_strict_region_anchor`를 추가했습니다.

## snapshot 결과

artifact:
- `docs/experiments/artifacts/exp-136-new-menu-friendly-strict-region-profile-snapshot.json`

요약:
- `accepted=true`
- `score=100.0`
- `detail_location_leak_count=0`
- `over_limit_scene_count=0`
- hook: `성수동에서 이거 보셨나요?`
- cta: `방문해 확인하기`

## 해석

1. `T01`은 더 이상 baseline coverage blind spot으로만 남아 있지 않습니다.
2. 현재 기준에서 `gpt-5-mini`는 `T01 new_menu / friendly / emphasizeRegion=true` 조건의 실용 profile로 재현 가능합니다.
3. 이 profile은 `main baseline` 대체가 아니라 `coverage candidate`입니다.
4. 즉 `T02 promotion` main baseline과 `T04 review` fallback option 사이에, `T01 new_menu` 전용 coverage option이 추가된 셈입니다.

## 판단

- `promptBaselineSummary` 관점에서 `T01` coverage를 실제로 연결할 최소 조건은 갖췄습니다.
- 다만 이 profile을 runtime provider routing과 자동 연결하는 일은 아직 별도 작업입니다.
- 현재 단계에서는 `recommendation metadata`와 `snapshot reproducibility`까지 확보한 것으로 보는 편이 맞습니다.

## 관련 파일

- `packages/template-spec/manifests/prompt-baseline-v1.json`
- `packages/template-spec/README.md`
- `scripts/run_prompt_baseline_snapshot.py`

# Test Scenario 138

## 제목

T01 new_menu friendly strict region profile snapshot

## 목적

- `EXP-135` 결과를 manifest option profile로 올린 뒤, snapshot runner로 재현 가능 상태인지 확인합니다.

## 고정 조건

- profile id: `new_menu_friendly_strict_region_anchor`
- source experiment: `EXP-135`
- selected model: `gpt-5-mini`

## 실행

1. manifest parse
   - `python -c "import json, pathlib; json.loads(pathlib.Path('packages/template-spec/manifests/prompt-baseline-v1.json').read_text(encoding='utf-8')); print('ok')"`
2. snapshot
   - `python scripts/run_prompt_baseline_snapshot.py --profile-id new_menu_friendly_strict_region_anchor`

## 기대 결과

- manifest parse가 통과합니다.
- snapshot artifact에 `accepted=true`, `score=100.0`, `detail_location_leak_count=0`가 기록됩니다.

## 이번 실행 결과

- artifact:
  - `docs/experiments/artifacts/exp-136-new-menu-friendly-strict-region-profile-snapshot.json`
- acceptance:
  - `accepted=true`
  - `required_score=100.0`
  - `required_detail_location_leak_count=0`
  - `allow_over_limit_scene_count=0`

## 판정

- `T01 new_menu / friendly / emphasizeRegion=true` coverage profile은 manifest option으로 재현 가능한 상태입니다.
- 이 profile은 main baseline 대체가 아니라 조건부 coverage candidate로 유지합니다.

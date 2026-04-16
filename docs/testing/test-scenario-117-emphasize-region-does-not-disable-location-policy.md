# Test Scenario 117 - emphasize region does not disable location policy

## 목적

- `EXP-115`에서 `emphasizeRegion=true`여도 `detailLocation` guard가 유지되는지 확인합니다.

## 입력 자료

1. `docs/experiments/artifacts/exp-01-slot-guidance-gemma4.json`
2. `docs/experiments/artifacts/exp-02-gemma-4-prompt-lever-experiment-audience-tone-guidance.json`
3. `services/worker/experiments/prompt_harness.py`
4. `apps/web/src/components/copy-policy-summary.tsx`
5. `docs/experiments/EXP-115-emphasize-region-does-not-disable-location-policy.md`

## 실행 명령

```bash
python scripts/rescore_location_surface_policy.py --artifact-path docs/experiments/artifacts/exp-01-slot-guidance-gemma4.json --source-experiment-id EXP-01
python scripts/rescore_location_surface_policy.py --artifact-path docs/experiments/artifacts/exp-02-gemma-4-prompt-lever-experiment-audience-tone-guidance.json --source-experiment-id EXP-02
python -m py_compile services/worker/experiments/prompt_harness.py
python -c "import json, pathlib; from services.worker.experiments.prompt_harness import evaluate_copy_bundle, get_experiment_definition, DEFAULT_TEMPLATE_SPEC_ROOT; from services.worker.adapters.template_loader import load_template, load_copy_rule; artifact=json.loads(pathlib.Path('docs/experiments/artifacts/exp-01-slot-guidance-gemma4.json').read_text(encoding='utf-8')); scenario=get_experiment_definition('EXP-01').scenario; row=artifact['results'][1]; template=load_template(DEFAULT_TEMPLATE_SPEC_ROOT, scenario.template_id); copy_rule=load_copy_rule(DEFAULT_TEMPLATE_SPEC_ROOT, scenario.purpose); result=evaluate_copy_bundle(row['output'], scenario, template, copy_rule); print(result['detail_location_policy_id'], result['detail_location_leak_count'], result['failed_checks'])"
npm run build:web
```

## 확인 포인트

1. `EXP-01`, `EXP-02` 모두 `public_copy_surfaces`, `distribution_surfaces`로 완화해도 Gemma 4 결과가 통과하지 않는지 확인합니다.
2. 직접 evaluation 결과에 `detail_location_policy_id = strict_all_surfaces`가 남는지 확인합니다.
3. `failed_checks`에 `nearby location leaked into strict region budget`가 포함되는지 확인합니다.
4. `copy-policy-summary.tsx` 설명 문구가 `지역명 강조 = detailLocation 공개 허용`으로 읽히지 않는지 확인합니다.

## 기대 결과

1. `emphasizeRegion=true`는 `detailLocation` guard를 끄는 조건이 아니라는 점이 재확인됩니다.
2. 앞으로 완화가 필요하면 evaluator 내부 예외가 아니라 명시적 policy mode로 다뤄야 한다는 기준이 고정됩니다.

# EXP-115 Emphasize region does not disable location policy

## 1. 기본 정보

- 실험 ID: `EXP-115`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `quick action semantics / evaluator policy mode / strict region baseline`

## 2. 왜 이 작업을 했는가

- 이전 단계까지는 `emphasizeRegion` quick action이 켜지면 evaluator의 `detailLocation` guard가 완전히 꺼지는 상태였습니다.
- 하지만 quick action의 planning 정의는 `지역명 강조`일 뿐, `상세 위치를 공개 copy에 더 써도 된다`는 의미는 아닙니다.
- 이번 단계에서는 `emphasizeRegion=true` 시나리오를 다시 점수화해, 정말 policy 완화가 필요한지부터 확인했습니다.

## 3. 확인 방법

대상 artifact:

1. `docs/experiments/artifacts/exp-01-slot-guidance-gemma4.json`
2. `docs/experiments/artifacts/exp-02-gemma-4-prompt-lever-experiment-audience-tone-guidance.json`

공통 조건:

- 둘 다 `T01 new_menu`
- `detailLocation = 서울숲 근처`
- `quick_options.emphasizeRegion = true`

재점수화 정책:

- `strict_all_surfaces`
- `public_copy_surfaces`
- `distribution_surfaces`

## 4. 결과

1. `EXP-01`
   - `Gemma 4` 2개 결과 모두
   - `strict_all_surfaces = fail`
   - `public_copy_surfaces = fail`
   - `distribution_surfaces = fail`
2. `EXP-02`
   - `Gemma 4` 2개 결과 모두
   - `strict_all_surfaces = fail`
   - `public_copy_surfaces = fail`
   - `distribution_surfaces = fail`

즉 `emphasizeRegion=true`인 `T01` 산출물에서도 nearby-location leakage는 이미 `captions/hashtags` 같은 공개 surface에 들어가 있었고, relaxed policy로 바꿔도 통과하지 못했습니다.

## 5. 실제 코드 변경

1. `services/worker/experiments/prompt_harness.py`
   - `should_enforce_detail_location_guard(scenario)`를 `detail_location` 존재 여부만 보도록 수정
   - `emphasizeRegion=true`여도 guard를 끄지 않도록 변경
   - evaluation 결과에 `detail_location_policy_id` 추가
2. `apps/web/src/components/copy-policy-summary.tsx`
   - `지역명 강조`는 `regionName` 강조용이며, `detailLocation` 공개 허용과는 별개라는 설명으로 수정
3. `packages/template-spec/README.md`
   - 현재 baseline에서는 `emphasizeRegion`이 켜져도 `locationPolicy` guard를 유지한다는 점 명시

## 6. 검증

실행:

```bash
python scripts/rescore_location_surface_policy.py --artifact-path docs/experiments/artifacts/exp-01-slot-guidance-gemma4.json --source-experiment-id EXP-01
python scripts/rescore_location_surface_policy.py --artifact-path docs/experiments/artifacts/exp-02-gemma-4-prompt-lever-experiment-audience-tone-guidance.json --source-experiment-id EXP-02
python -m py_compile services/worker/experiments/prompt_harness.py
python -c "import json, pathlib; from services.worker.experiments.prompt_harness import evaluate_copy_bundle, get_experiment_definition, DEFAULT_TEMPLATE_SPEC_ROOT; from services.worker.adapters.template_loader import load_template, load_copy_rule; artifact=json.loads(pathlib.Path('docs/experiments/artifacts/exp-01-slot-guidance-gemma4.json').read_text(encoding='utf-8')); scenario=get_experiment_definition('EXP-01').scenario; row=artifact['results'][1]; template=load_template(DEFAULT_TEMPLATE_SPEC_ROOT, scenario.template_id); copy_rule=load_copy_rule(DEFAULT_TEMPLATE_SPEC_ROOT, scenario.purpose); result=evaluate_copy_bundle(row['output'], scenario, template, copy_rule); print(result['detail_location_policy_id'], result['detail_location_leak_count'], result['failed_checks'])"
npm run build:web
```

핵심 확인:

- `EXP-01`, `EXP-02` 모두 relaxed policy가 효과가 없었습니다.
- 직접 evaluation 결과에서도 `detail_location_policy_id = strict_all_surfaces`와 `nearby location leaked into strict region budget`가 확인됐습니다.

## 7. 결론

- `emphasizeRegion` quick action은 `regionName`을 더 세게 쓰는 change set이지, `detailLocation` 공개 노출 허용 신호가 아닙니다.
- 따라서 현재 baseline에서는 `emphasizeRegion=true`여도 `locationPolicy` guard를 유지하는 것이 맞습니다.
- 만약 추후 일부 템플릿에서만 완화가 필요하다면, evaluator에서 암묵적으로 끄는 대신 `policyId`를 명시적으로 바꾸는 구조로 가야 합니다.

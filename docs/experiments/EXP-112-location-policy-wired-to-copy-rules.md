# EXP-112 Location policy wired to copy-rules

## 1. 기본 정보

- 실험 ID: `EXP-112`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `copy-rule integration / evaluation policy layer / strict region baseline`

## 2. 왜 이 작업을 했는가

- `EXP-110`, `EXP-111`까지는 nearby-location leakage를 막는 기준과 surface 정책을 draft/실험 수준으로만 다뤘습니다.
- 하지만 본선 기준선을 유지하려면 이 정책이 `copy-rule` 또는 별도 evaluation layer에 실제로 연결돼 있어야 합니다.
- 이번 단계에서는 우선 `copy-rule.locationPolicy`를 읽도록 평가기를 연결하고, `promotion`, `review` 규칙에 `strict_all_surfaces`를 명시했습니다.

## 3. 실제 연결 내용

1. `services/worker/experiments/prompt_harness.py`
   - `copy_rule.locationPolicy.forbiddenDetailLocationSurfaces`를 읽어 detail-location leakage surface를 결정하도록 변경
   - evaluation 결과에 아래 필드를 함께 남기도록 확장
     - `detail_location_policy_surfaces`
     - `detail_location_leaks_by_surface`
2. `packages/template-spec/copy-rules/promotion.json`
   - `locationPolicy.policyId = strict_all_surfaces`
3. `packages/template-spec/copy-rules/review.json`
   - `locationPolicy.policyId = strict_all_surfaces`

## 4. 검증

실행:

```bash
python -m py_compile services/worker/experiments/prompt_harness.py
python scripts/run_model_comparison_experiment.py --experiment-id EXP-108
```

확인:

- `gpt-5-mini` evaluation에 아래 값이 실제로 들어갔습니다.
  - `detail_location_policy_surfaces`
  - `detail_location_leak_count`
  - `detail_location_leaks_by_surface`
- 최신 `EXP-108` 결과에서는 `gpt-5-mini`가 `captions: 1`로 leakage가 기록됐습니다.
- `Gemma 4`는 같은 strict prompt에서 `failed_checks = []`를 유지했습니다.

## 5. 해석

- 이제 nearby-location policy는 draft 문서만이 아니라 실제 평가 기준선으로 연결된 상태입니다.
- 아직 runtime generation이 이 policy를 직접 소비하는 것은 아니지만, 적어도 실험 평가 기준은 canonical template-spec 쪽으로 한 단계 더 이동했습니다.

## 6. 결론

- strict region baseline에서는 `locationPolicy`를 copy-rule 레벨에 두는 방향이 현재 구조와 가장 잘 맞습니다.
- 다음 단계는 이 policy를:
  1. `copy-rule`에서 계속 관리할지
  2. 별도 `evaluation policy` 레이어로 독립시킬지
정하는 일입니다.

## 7. 다음 액션

1. 현재는 `promotion`, `review`만 명시했으므로, 나머지 purpose에 이 policy가 필요한지 판단합니다.
2. worker runtime이나 editor preview에서도 이 policy를 보여줄 필요가 있는지 검토합니다.

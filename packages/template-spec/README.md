# Template Spec

템플릿 규칙 데이터 보관 위치입니다.

- 템플릿 메타데이터
- 컷 구성 규칙
- 스타일 규칙
- 카피 규칙 연결 정보

## 구조

```text
template-spec/
├─ templates/
├─ styles/
├─ copy-rules/
└─ manifests/
```

## 사용 원칙

1. 템플릿 추가 시 `manifests/template-map.json`도 같이 수정합니다.
2. 템플릿은 코드로 하드코딩하지 않고 JSON 데이터로 관리합니다.
3. 스타일 프리셋은 템플릿과 분리합니다.
4. purpose별 카피 규칙은 `copy-rules/`에서 관리합니다.
5. quick action/change set 호환성은 `template-map.json`과 각 템플릿의 `changeSetCompatibility`를 함께 봅니다.
6. `manifests/slot-layer-map.json`은 scene/textRole을 `hook / body / cta` 레이어로 재해석하는 비파괴 manifest입니다.
7. 현재 source of truth는 여전히 `templates/*.json`이지만, runtime은 이 manifest를 읽어 `copyDeck`, `sceneLayerSummary` 같은 파생 metadata를 함께 만듭니다.
8. `manifests/reference-hook-pack-v1.json`은 외부 광고 레퍼런스에서 뽑아낸 hook 후보 초안입니다.
9. 이 hook pack도 현재 runtime이 직접 읽지 않는 proposal 데이터이며, 추후 copy generation 또는 editor UI 실험에 연결할 수 있습니다.
10. `manifests/location-surface-policy-v1.json`은 strict region 시나리오에서 nearby-location leakage를 어떤 surface 기준으로 금지할지 정리한 draft 정책 manifest입니다.
11. 이 정책 manifest도 현재 runtime 미사용 초안이며, evaluation policy와 copy-rule 확장 논의의 기준면으로 사용합니다.
12. 현재 `copy-rules/new_menu.json`, `promotion.json`, `location_push.json`, `review.json`은 모두 이 draft와 정렬된 `locationPolicy` 필드를 포함하고 있으며, prompt harness evaluation이 이를 직접 읽습니다.
13. `emphasizeRegion` quick action은 `regionName`을 더 세게 쓰는 change set이며, `detailLocation` 공개 노출 허용으로 해석하지 않습니다.
14. 따라서 현재 baseline에서는 `emphasizeRegion`이 켜져도 `locationPolicy` guard를 유지하고, 별도 완화가 필요하면 policy mode를 명시적으로 추가해야 합니다.
15. `manifests/prompt-baseline-v1.json`은 현재 prompt/model 기준선을 고정한 draft manifest입니다.
16. 현재 기준선은 `T02 promotion / b_grade_fun / strict_all_surfaces / Gemma 4` 조합이며, 실험 근거는 `EXP-108`, `EXP-109`, `EXP-110`입니다.
17. 같은 manifest 안의 `baselineOptions[]`에는 main baseline 외의 조건부 profile도 넣을 수 있습니다.
18. 현재는 `review_strict_fallback_surface_lock`, `review_strict_fallback_surface_lock_shorter_copy_off`, `review_strict_fallback_surface_lock_highlight_price_shorter_copy_off`, `review_strict_fallback_surface_lock_highlight_price`, `review_strict_fallback_surface_lock_region_anchor`, `review_strict_fallback_surface_lock_shorter_copy_off_region_anchor`, `review_strict_fallback_surface_lock_highlight_price_shorter_copy_off_region_anchor`, `review_strict_fallback_surface_lock_highlight_price_region_anchor`, `new_menu_friendly_minimal_region_anchor`, `new_menu_friendly_minimal_region_anchor_shorter_copy`, `new_menu_friendly_minimal_region_anchor_highlight_price`, `new_menu_friendly_minimal_region_anchor_highlight_price_shorter_copy`, `new_menu_friendly_strict_region_anchor`, `new_menu_friendly_region_anchor_shorter_copy`, `new_menu_friendly_region_anchor_highlight_price`, `new_menu_friendly_region_anchor_highlight_price_shorter_copy`, `promotion_surface_lock_shorter_copy_off`, `promotion_surface_lock_highlight_price_off`, `promotion_surface_lock_highlight_price_off_shorter_copy_off`, `promotion_surface_lock_highlight_price_off_shorter_copy_off_region_anchor`, `promotion_surface_lock_highlight_price_off_region_anchor`, `promotion_surface_lock_shorter_copy_off_region_anchor`, `promotion_surface_lock_region_anchor` profile이 추가돼 있습니다.
19. `review_strict_fallback_surface_lock`은 `T04 review`에서 `gpt-5-mini`를 strict fallback candidate로 쓰는 옵션입니다.
20. `review_strict_fallback_surface_lock_shorter_copy_off`는 `T04 review / shorterCopy=false`에서 `gpt-5-mini`를 strict fallback candidate로 쓰는 옵션입니다.
21. `review_strict_fallback_surface_lock_highlight_price_shorter_copy_off`는 `T04 review / highlightPrice=true / shorterCopy=false`에서 `gpt-5-mini`를 strict fallback candidate로 쓰는 옵션입니다.
22. `review_strict_fallback_surface_lock_highlight_price`는 `T04 review / highlightPrice=true / shorterCopy=true`에서 `gpt-5-mini`를 strict fallback candidate로 쓰는 옵션입니다.
23. `review_strict_fallback_surface_lock_region_anchor`는 `T04 review / highlightPrice=false / shorterCopy=true / emphasizeRegion=true`에서 `gpt-5-mini`를 strict fallback candidate로 쓰는 옵션입니다.
24. `review_strict_fallback_surface_lock_shorter_copy_off_region_anchor`는 `T04 review / highlightPrice=false / shorterCopy=false / emphasizeRegion=true`에서 `gpt-5-mini`를 strict fallback candidate로 쓰는 옵션입니다.
25. `review_strict_fallback_surface_lock_highlight_price_shorter_copy_off_region_anchor`는 `T04 review / highlightPrice=true / shorterCopy=false / emphasizeRegion=true`에서 `gpt-5-mini`를 strict fallback candidate로 쓰는 옵션입니다.
26. `review_strict_fallback_surface_lock_highlight_price_region_anchor`는 `T04 review / highlightPrice=true / shorterCopy=true / emphasizeRegion=true`에서 `gpt-5-mini`를 strict fallback candidate로 쓰는 옵션입니다.
27. `new_menu_friendly_minimal_region_anchor`는 `T01 new_menu / friendly / emphasizeRegion=false`에서 `gpt-5-mini`를 coverage candidate로 쓰는 옵션입니다.
28. 이 profile은 region을 완전히 제거하지 않고, copy-rule 최소치에 맞춰 caption 1개와 `#성수동` 1개만 남기는 minimal anchor 기준입니다.
29. `new_menu_friendly_minimal_region_anchor_shorter_copy`는 `T01 new_menu / friendly / shorterCopy=true / emphasizeRegion=false`에서 `gpt-5-mini`를 coverage candidate로 쓰는 옵션입니다.
30. 이 profile은 minimal anchor를 유지한 채 scene/caption을 한 포인트씩 더 짧게 압축하는 기준입니다.
31. `new_menu_friendly_minimal_region_anchor_highlight_price`는 `T01 new_menu / friendly / highlightPrice=true / emphasizeRegion=false`에서 `gpt-5-mini`를 coverage candidate로 쓰는 옵션입니다.
32. 이 profile은 minimal anchor를 유지한 채 가격 숫자 없이 메뉴 가치 포인트를 더 앞세우는 기준입니다.
33. `new_menu_friendly_minimal_region_anchor_highlight_price_shorter_copy`는 `T01 new_menu / friendly / highlightPrice=true / shorterCopy=true / emphasizeRegion=false`에서 `gpt-5-mini`를 coverage candidate로 쓰는 옵션입니다.
34. 이 profile은 minimal anchor를 유지한 채 한 줄 가치 포인트만 짧게 foreground로 남기는 기준입니다.
35. `new_menu_friendly_strict_region_anchor`는 `T01 new_menu / friendly / emphasizeRegion=true`에서 `gpt-5-mini`를 coverage candidate로 쓰는 옵션입니다.
36. `new_menu_friendly_region_anchor_shorter_copy`는 `T01 new_menu / friendly / shorterCopy=true / emphasizeRegion=true`에서 `gpt-5-mini`를 coverage candidate로 쓰는 옵션입니다.
37. `new_menu_friendly_region_anchor_highlight_price`는 `T01 new_menu / friendly / highlightPrice=true / emphasizeRegion=true`에서 `gpt-5-mini`를 coverage candidate로 쓰는 옵션입니다.
38. `new_menu_friendly_region_anchor_highlight_price_shorter_copy`는 `T01 new_menu / friendly / highlightPrice=true / shorterCopy=true / emphasizeRegion=true`에서 `gpt-5-mini`를 coverage candidate로 쓰는 옵션입니다.
39. `promotion_surface_lock_shorter_copy_off`는 `T02 promotion / shorterCopy=false`에서 `Gemma 4`를 coverage candidate로 쓰는 옵션입니다.
40. `promotion_surface_lock_highlight_price_off`는 `T02 promotion / highlightPrice=false`에서 `Gemma 4`를 coverage candidate로 쓰는 옵션입니다.
41. `promotion_surface_lock_highlight_price_off_shorter_copy_off`는 `T02 promotion / highlightPrice=false / shorterCopy=false`에서 `Gemma 4`를 coverage candidate로 쓰는 옵션입니다.
42. `promotion_surface_lock_highlight_price_off_shorter_copy_off_region_anchor`는 `T02 promotion / highlightPrice=false / shorterCopy=false / emphasizeRegion=true`에서 `Gemma 4`를 coverage candidate로 쓰는 옵션입니다.
43. `promotion_surface_lock_highlight_price_off_region_anchor`는 `T02 promotion / highlightPrice=false / shorterCopy=true / emphasizeRegion=true`에서 `Gemma 4`를 coverage candidate로 쓰는 옵션입니다.
44. `promotion_surface_lock_shorter_copy_off_region_anchor`는 `T02 promotion / highlightPrice=true / shorterCopy=false / emphasizeRegion=true`에서 `Gemma 4`를 coverage candidate로 쓰는 옵션입니다.
45. `promotion_surface_lock_region_anchor`는 `T02 promotion / highlightPrice=true / shorterCopy=true / emphasizeRegion=true`에서 `Gemma 4`를 coverage candidate로 쓰는 옵션입니다.
46. `scripts/run_prompt_baseline_snapshot.py --profile-id <profileId>`로 main baseline 외의 option profile도 snapshot 재현이 가능합니다.
47. Google 계열 profile은 필요하면 `--timeout-sec`, `--max-retries`, `--retry-backoff-sec`를 같이 넘겨 transport recommendation을 반영할 수 있습니다.
48. worker runtime은 `manifests/prompt-baseline-v1.json`을 읽어 `promptBaselineSummary`를 결과 payload/render-meta에 같이 붙입니다.
49. 이 summary는 recommendation metadata이며, 현재 deterministic runtime의 실제 generation provider routing을 자동으로 바꾸지는 않습니다.
50. 같은 manifest의 `operationalChecks[]`에는 timeout/retry 같은 운영성 spot check 결과도 같이 남길 수 있습니다.
51. 필요한 경우 각 `operationalChecks[]` 항목에는 `selectedModel`, `transportRecommendation`을 함께 넣어, 어떤 모델에 어떤 retry guard가 붙는지 recommendation metadata로 구조화할 수 있습니다.

# Test Scenario 113 - nearby-location surface policy matrix

## 목적

- `EXP-111`에서 surface 정책을 바꿔도 strict region 모델 판단이 실제로 달라지는지 확인합니다.

## 입력 자료

1. `scripts/rescore_location_surface_policy.py`
2. `packages/template-spec/manifests/location-surface-policy-v1.json`
3. `docs/experiments/EXP-111-nearby-location-surface-policy-matrix.md`

## 실행 명령

```bash
python scripts/rescore_location_surface_policy.py --artifact-path docs/experiments/artifacts/exp-108-repeatability.json --source-experiment-id EXP-108
```

## 확인 포인트

1. `strict_all_surfaces`, `public_copy_surfaces`, `distribution_surfaces` 3개 정책이 모두 계산되는지 확인합니다.
2. `Gemma 4`가 모든 정책에서 통과하는지 확인합니다.
3. `gpt-5-mini`가 느슨한 정책에서도 captions/hashtags leakage 때문에 계속 탈락하는지 확인합니다.

## 기대 결과

1. policy를 완화해도 현재 결론은 바뀌지 않습니다.
2. 따라서 strict region 기본 정책을 `strict_all_surfaces`로 두는 판단이 유지됩니다.

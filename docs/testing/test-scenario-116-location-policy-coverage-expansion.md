# Test Scenario 116 - location policy coverage expansion

## 목적

- `EXP-114`에서 `T01 new_menu`, `T03 location_push`에도 `locationPolicy`가 확장됐는지 확인합니다.

## 입력 자료

1. `packages/template-spec/copy-rules/new_menu.json`
2. `packages/template-spec/copy-rules/location_push.json`
3. `apps/web/src/components/copy-policy-summary.tsx`
4. `docs/experiments/EXP-114-location-policy-coverage-expansion.md`

## 실행 명령

```bash
python -c "import json, pathlib; [json.loads(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['packages/template-spec/copy-rules/new_menu.json','packages/template-spec/copy-rules/location_push.json']]; print('ok')"
npm run build:web
```

## 확인 포인트

1. `new_menu.json`, `location_push.json`에 `locationPolicy.policyId = strict_all_surfaces`가 있는지 확인합니다.
2. `copy-policy-summary.tsx`가 `emphasizeRegion` quick action 보유 템플릿에 대해 `regionName` 강조용이며 `detailLocation` 공개 허용과는 별개라는 문구를 출력하는지 확인합니다.
3. web build가 타입 오류 없이 통과하는지 확인합니다.

## 기대 결과

1. `locationPolicy` coverage가 `T01`~`T04` 전체로 맞춰집니다.
2. `policy exists`와 `emphasizeRegion`의 의미가 UI 설명으로 분리됩니다.

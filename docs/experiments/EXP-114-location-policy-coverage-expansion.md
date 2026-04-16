# EXP-114 Location policy coverage expansion

## 1. 기본 정보

- 실험 ID: `EXP-114`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `copy-rule coverage / template-spec alignment / strict region policy`

## 2. 왜 이 작업을 했는가

- `EXP-113`까지는 `T02 promotion`, `T04 review`만 `locationPolicy`가 연결돼 있었고, `T01 new_menu`, `T03 location_push`는 UI에서 `상세 위치 정책 미연결`로 보였습니다.
- 하지만 planning 문서 기준으로 공개 copy 구조는 네 목적 모두 `regionName` 중심이며, `detailLocation`은 선택 입력일 뿐 public surface의 canonical slot으로 정의되지 않았습니다.
- 따라서 이번 단계에서는 `T01`, `T03`에도 동일한 `strict_all_surfaces` 정책을 확장해, copy-rule coverage를 purpose 전체로 맞췄습니다.

## 3. 판단 근거

1. `docs/planning/02_USER_FLOW_AND_SCREEN_POLICY.md`
   - `detailLocation`은 선택 입력입니다.
2. `docs/planning/03_CONTENT_PIPELINE_AND_TEMPLATE_SPEC.md`
   - `new_menu`: `후킹 + 메뉴명 + 차별점 + CTA`
   - `location_push`: `지역명 + 방문 이유 + CTA`
   - 즉 canonical copy 구조는 `regionName` 중심이지 `detailLocation` 중심이 아닙니다.
3. 기존 산출물 확인
   - `EXP-01`, `EXP-02`에서는 `T01` 산출물에 `서울숲 근처`, `#서울숲데이트`가 섞인 사례가 있었습니다.
   - 이는 `detailLocation`이 별도 통제 없이 public copy에 흘러들 수 있다는 신호입니다.

## 4. 실제 변경

1. `packages/template-spec/copy-rules/new_menu.json`
   - `locationPolicy.policyId = strict_all_surfaces`
2. `packages/template-spec/copy-rules/location_push.json`
   - `locationPolicy.policyId = strict_all_surfaces`
3. `apps/web/src/components/copy-policy-summary.tsx`
   - `emphasizeRegion` quick action이 있는 템플릿은
   - `regionName` 강조용 quick action이며 `detailLocation` 공개 허용과는 별개라는 점을 함께 표시하도록 보강

## 5. 해석

- 이제 네 목적 모두에서 `detailLocation`은 기본적으로 public copy surface에 직접 노출하지 않는 방향으로 정렬됐습니다.
- 다만 `emphasizeRegion` quick action이 있는 `T01`, `T03`는 regionName을 더 세게 쓰는 재생성 흐름이 있으므로, 이후 단계에서 `active policy mode`를 별도로 판단할 필요가 있습니다.

## 6. 검증

실행:

```bash
python -c "import json, pathlib; [json.loads(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['packages/template-spec/copy-rules/new_menu.json','packages/template-spec/copy-rules/location_push.json']]; print('ok')"
npm run build:web
```

결과:

- `new_menu.json`, `location_push.json` JSON 파싱이 정상 통과했습니다.
- `build:web`도 정상 통과했습니다.

## 7. 결론

- `locationPolicy` coverage는 이제 `T01`~`T04` 전체로 확장됐습니다.
- 다음 단계는:
  1. `emphasizeRegion` quick action 시 runtime/evaluator가 실제로 어떤 policy mode를 써야 하는지 명시적으로 분리할지
  2. 결과 payload나 scene preview에 `policy active/inactive` 상태까지 보여줄지
정하는 것입니다.

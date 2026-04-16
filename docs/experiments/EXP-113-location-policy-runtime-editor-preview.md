# EXP-113 Location policy runtime/editor preview

## 1. 기본 정보

- 실험 ID: `EXP-113`
- 작성일: `2026-04-10`
- 작성자: Codex
- 관련 축: `web runtime visibility / editor preview / copy-rule transparency`

## 2. 왜 이 작업을 했는가

- `EXP-112`까지로 nearby-location policy는 `copy-rule`과 evaluation에 연결됐습니다.
- 하지만 본선 제품 흐름에서는 이 정책이 화면에 보이지 않아, 어떤 템플릿이 `strict_all_surfaces`를 쓰는지 팀이 즉시 확인하기 어려웠습니다.
- 이번 단계에서는 메인 workbench와 history 화면에서 현재 template/purpose 기준 `region budget`과 `detail location forbidden surfaces`를 바로 노출해, 정책 기준선을 UI에서도 확인할 수 있게 했습니다.

## 3. 실제 변경

1. `apps/web/src/lib/contracts.ts`
   - `CopyRule` 타입에 아래 필드를 반영
     - `locationPolicy`
     - `templateIds`
     - `supportedQuickActions`
   - `findCopyRule(templateId, purpose)` helper 추가
2. `apps/web/src/components/copy-policy-summary.tsx`
   - `copy-rule`을 읽어 아래를 요약하는 공통 카드 추가
     - `regionPolicy.minSlots / maxRepeat`
     - `locationPolicy.policyId`
     - `forbiddenDetailLocationSurfaces`
     - `supportedQuickActions`
3. `apps/web/src/components/demo-workbench.tsx`
   - 편집 단계의 `현재 템플릿 카피 정책` 카드 추가
   - 결과 패널의 `결과 기준 카피 정책` 카드 추가
4. `apps/web/src/components/history-board.tsx`
   - `result.video.templateId` 기준으로 `최근 결과 카피 정책` 카드 추가

## 4. 확인된 동작

1. `T02 promotion`, `T04 review`
   - `strict_all_surfaces` badge가 보이고
   - `hook / CTA / captions / hashtags / scene text / sub text`가 금지 surface로 표시됩니다.
2. `T01 new_menu`, `T03 location_push`
   - 현재 `locationPolicy`가 선언되지 않았기 때문에
   - UI에서 `상세 위치 정책 미연결`로 보입니다.

## 5. 검증

실행:

```bash
npm run build:web
```

결과:

- Next.js build가 정상 통과했습니다.
- 새 카드 컴포넌트와 `CopyRule` 타입 확장으로 인한 타입 오류는 없었습니다.

## 6. 해석

- nearby-location 정책이 이제 문서와 평가기뿐 아니라 `web runtime`에서도 visible state가 됐습니다.
- 동시에 어떤 purpose/template 조합은 아직 `locationPolicy`가 빠져 있는지도 화면에서 바로 드러납니다.
- 즉 이번 단계는 정책을 더 강하게 만든 작업이 아니라, `현재 기준선 coverage gap`을 제품 화면에서도 보이게 만든 작업입니다.

## 7. 결론

- `strict region` 관련 기준은 앞으로 UI에서도 확인 가능한 canonical rule로 다룰 수 있습니다.
- 다음 단계는 두 가지 중 하나입니다.
  1. `T01`, `T03`에도 `locationPolicy`가 필요한지 판단한다.
  2. 현재 UI 노출을 토대로, quick action이나 scene preview가 이 정책을 직접 참조할 필요가 있는지 검토한다.

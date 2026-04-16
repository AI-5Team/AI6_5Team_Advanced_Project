# Test Scenario 115 - location policy runtime/editor preview

## 목적

- `EXP-113`에서 `copy-rule.locationPolicy`가 메인 편집 화면과 history 화면에 실제로 노출되는지 확인합니다.

## 입력 자료

1. `apps/web/src/lib/contracts.ts`
2. `apps/web/src/components/copy-policy-summary.tsx`
3. `apps/web/src/components/demo-workbench.tsx`
4. `apps/web/src/components/history-board.tsx`
5. `docs/experiments/EXP-113-location-policy-runtime-editor-preview.md`

## 실행 명령

```bash
npm run build:web
```

## 확인 포인트

1. `demo-workbench`에서 현재 선택한 template/purpose 기준 정책 카드가 렌더 가능한지 확인합니다.
2. `history-board`에서 `result.video.templateId` 기준 정책 카드가 렌더 가능한지 확인합니다.
3. `T02`, `T04`는 `strict_all_surfaces`와 금지 surface 목록이 보이는지 확인합니다.
4. `T01`, `T03`는 아직 `상세 위치 정책 미연결`로 표시되는지 확인합니다.

## 기대 결과

1. nearby-location 정책이 평가기뿐 아니라 runtime/editor UI에서도 visible state가 됩니다.
2. 현재 어떤 템플릿이 canonical policy에 연결됐고, 어떤 템플릿은 아직 미연결인지 화면에서 바로 구분할 수 있습니다.

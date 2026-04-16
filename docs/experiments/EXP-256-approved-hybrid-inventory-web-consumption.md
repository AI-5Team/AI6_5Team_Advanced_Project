# EXP-256 Approved Hybrid Inventory Web Consumption

## 1. 기본 정보

- 실험 ID: `EXP-256`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `approved hybrid inventory를 web generate 흐름에서 실제로 선택/소비`

## 2. 왜 이 작업을 했는가

- `EXP-255`까지로 approved inventory는 API에서 읽을 수 있었지만, 실제 web generate 진입점에서는 아직 이 기준선을 소비하지 못했습니다.
- 이 상태에서는 approved inventory가 있어도 운영자는 계속 문서와 candidate key를 수동 대조해야 했고, 본선 흐름에는 연결되지 않은 상태였습니다.
- 이번 작업의 목적은 새 판단 로직을 늘리는 것이 아니라, 이미 고정된 approved inventory를 web 생성 마법사에서 직접 선택해 generate/regenerate 요청에 태울 수 있게 만드는 것입니다.

## 3. 이번에 바꾼 것

1. `packages/contracts/schemas/generation.ts`
   - `GenerateProjectRequest`, `ChangeSet`에 `approvedHybridSourceCandidateKey`를 추가했습니다.
   - `RendererSummary`에도 `hybridSourceSelectionMode`, `hybridSourceCandidateKey`를 추가해 API 응답과 web contract를 맞췄습니다.
2. `apps/web/src/app/api/hybrid-candidates/approved/route.ts`
   - local demo 환경에서도 `docs/experiments/artifacts/exp-254-approved-hybrid-candidate-inventory/report.json`을 읽어 `/api/hybrid-candidates/approved`를 제공하도록 추가했습니다.
   - `label`, `serviceLane` query와 lane/label별 추천 재계산도 함께 붙였습니다.
3. `apps/web/src/lib/api.ts`, `apps/web/src/lib/contracts.ts`
   - approved inventory 응답 타입과 `listApprovedHybridCandidates()` 호출 함수를 추가했습니다.
4. `apps/web/src/components/demo-workbench.tsx`
   - 생성 마법사 2단계에 `승인된 hybrid 기준선 선택` UI를 추가했습니다.
   - recommended lane 버튼, 전체 candidate select, 현재 선택 요약을 붙였습니다.
   - generate/regenerate 요청에 선택된 `approvedHybridSourceCandidateKey`를 함께 보내도록 정리했습니다.
   - 결과 화면에도 현재 적용된 hybrid baseline key를 표시하도록 보강했습니다.
5. `apps/web/src/lib/demo-store.ts`
   - local demo 모드에서도 initial generation 시 approved candidate key가 snapshot에서 사라지지 않도록 보존했습니다.
   - 결과의 `rendererSummary`도 hybrid source 사용 여부를 반영하도록 맞췄습니다.

## 4. 실행 및 검증

### 4.1 타입 체크

```bash
npm run lint:web
```

결과:

- `tsc --noEmit` 통과

### 4.2 production build

```bash
npm run build:web
```

결과:

- `next build` 통과
- route 목록에 `ƒ /api/hybrid-candidates/approved`가 추가된 것을 확인했습니다.

## 5. 결과

1. 이제 web generate 진입점에서도 approved inventory를 직접 읽고 candidate를 선택할 수 있습니다.
2. local demo API를 쓰는 경우에도 `EXP-254` artifact를 그대로 읽으므로, 문서와 UI의 기준선이 분리되지 않습니다.
3. generate/regenerate 모두 선택된 `approvedHybridSourceCandidateKey`를 보낼 수 있고, 결과 화면에서도 어떤 baseline이 적용됐는지 다시 확인할 수 있습니다.
4. 이번 단계에서는 의도적으로 `자동 선택`을 넣지 않았습니다.
   - lane 추론이 아직 불안정한 상태에서 자동으로 candidate를 강제 적용하면, 기준선 소비와 잘못된 자동화가 섞여 버리기 때문입니다.

## 6. 해석

1. `EXP-255`까지의 inventory read path는 “읽을 수 있음” 단계였고, `EXP-256`으로 비로소 “web에서 실제로 쓸 수 있음” 단계까지 닫혔습니다.
2. 이로써 approved hybrid baseline은 문서용 메모가 아니라, generate UI에서 명시적으로 선택 가능한 운영 기준선이 됐습니다.
3. 지금 다음 우선순위는 UI를 더 화려하게 만드는 것이 아니라, 실제 운영자가 어떤 lane에서 어떤 candidate를 선택해야 하는지 판단 기준을 더 명확히 하는 것입니다.

## 7. 결론

- approved hybrid inventory는 이제 API, local demo route, web generate UI까지 일관되게 연결됐습니다.
- 따라서 다음 단계는 `candidate 자동 추천 기준 보강` 또는 `tray/full-plate lane inventory 확장` 중 하나여야 하며, 단순히 새 inventory 레이어를 또 만드는 일은 우선순위가 아닙니다.

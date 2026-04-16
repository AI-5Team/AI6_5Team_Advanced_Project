# EXP-41 Quick Action Visible Delta - shorterCopy

## 1. 기본 정보

- 실험 ID: `EXP-41`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `서비스 본선 quick action 검증`

## 2. 왜 이 작업을 했는가

- 중간 점검에서 `quick action visible delta`가 본선 검증 우선순위로 다시 올라왔습니다.
- 따라서 실제 프로젝트 생성 후 `문구 더 짧게(shorterCopy)`만 적용했을 때 결과 차이가 눈에 보이는지 end-to-end로 확인했습니다.

## 3. baseline

### 고정한 조건

1. 입력: 실제 샘플 사진 `규카츠`, `맥주`
2. 업종/목적/스타일: `restaurant / promotion / b_grade_fun`
3. 템플릿: `T02`
4. baseline quick options: `highlightPrice=false`, `shorterCopy=false`, `emphasizeRegion=false`
5. 바뀐 변수: regenerate change set의 `shorterCopy=true`만 변경

## 4. 무엇을 바꿨는가

- `scripts/capture_quick_action_delta.mjs`
  - 프로젝트 생성 -> 실제 사진 업로드 -> generate -> scene frame capture
  - 이후 같은 프로젝트에 `shorterCopy=true`로 regenerate
  - baseline/variant 전후를 캡처하고 요약 JSON 저장
- `apps/web/src/lib/demo-store.ts`
  - regenerate의 `changeSet` 값이 `buildCopyBundle`에 실제 반영되도록 수정
  - `shorterCopy`가 hook/caption에 가시적으로 영향을 주도록 worker baseline과 더 가깝게 정렬
- `apps/web/src/lib/scene-plan.ts`
  - `scene-frame?projectId=`가 외부 `127.0.0.1:8000`이 아니라 같은 web 서버의 `/api/projects/...`를 보도록 수정

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-41-quick-action-visible-delta/summary.json`
- `docs/experiments/artifacts/exp-41-quick-action-visible-delta/baseline-opening.png`
- `docs/experiments/artifacts/exp-41-quick-action-visible-delta/shorter-copy-opening.png`
- `docs/experiments/artifacts/exp-41-quick-action-visible-delta/baseline-closing.png`
- `docs/experiments/artifacts/exp-41-quick-action-visible-delta/shorter-copy-closing.png`

### baseline 대비 차이

- hookText 길이: `-11`
- opening primaryText 길이: `-11`
- opening caption 길이: `19 -> 17`
- 시각 비교
  - baseline: `성수동 기준으로 오늘만 놓치기 아쉬운 혜택 흐름을 한 번에 …`
  - variant: `성수동 기준으로 오늘만 놓치기 아쉬운 혜택`

### 확인된 것

1. `shorterCopy`는 이제 실제 regenerate 결과에 반영됩니다.
2. 전후 opening scene에서 문구 길이 차이가 눈에 보입니다.
3. 본선 기준에서 가장 중요한 사실은, 이번 작업으로 `quick action` 경로가 “눌러도 변화 없음” 상태에서 벗어났다는 점입니다.

## 6. 실패/제약

1. 최초 점검에서는 delta가 `0`이었고, scene-frame 캡처도 오류 페이지가 찍혔습니다.
2. 원인은 두 가지였습니다.
   - web demo regenerate가 `changeSet.shorterCopy`를 실제 copy builder에 반영하지 않음
   - `scene-frame?projectId=`가 외부 API base를 보다가 실패
3. 즉 이번 실험은 단순 검증이 아니라 본선 버그 수정까지 포함합니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `shorterCopy`는 이제 본선에서 “눈에 보이는 delta”를 만듭니다.
  - quick action 검증은 계속 같은 방식으로 `highlightPrice`, `emphasizeRegion`도 이어갈 수 있습니다.

## 8. 다음 액션

1. 다음 quick action 본선 점검은 `highlightPrice` 또는 `emphasizeRegion`입니다.
2. `scene-frame?projectId=` 경로는 이제 다른 end-to-end 캡처에도 재사용할 수 있습니다.

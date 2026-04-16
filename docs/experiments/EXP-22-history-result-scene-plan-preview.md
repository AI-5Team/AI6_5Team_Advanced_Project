# EXP-22 History Result ScenePlan Preview

## 1. 기본 정보

- 실험 ID: `EXP-22`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `history/result surface`의 `scenePlan` preview 연결

## 2. 왜 이 작업을 했는가

- `EXP-21`로 main workbench는 실제 `project result.scenePlan`을 직접 소비하게 됐습니다.
- 하지만 이력 화면은 여전히 결과 요약 텍스트만 보여 주고 있어서, 서비스 루프 기준으로는 확인 surface가 두 갈래로 나뉘어 있었습니다.
- 이번 작업의 목적은 `history` 화면도 같은 `scenePlan preview` 경로를 쓰게 만들어, 결과 확인 경험을 메인 화면과 맞추는 것이었습니다.

## 3. baseline

### 이전 baseline

1. `history` 화면은 `hookText`, `ctaText`, `hashtags`만 보여 줬습니다.
2. `scene-frame`으로 이어지는 링크는 없었습니다.
3. 기본 선택 프로젝트가 `생성 중` 항목에 걸리면, 새 result preview가 보이지 않는 문제가 있었습니다.

### 이번에 고정한 조건

1. renderer나 prompt는 바꾸지 않았습니다.
2. 바꾼 것은 `result surface` 하나뿐입니다.
3. 동일한 `project result.scenePlan` source를 main/history 둘 다 쓰도록 맞췄습니다.

## 4. 무엇을 바꿨는가

- `apps/web/src/components/scene-plan-preview-links.tsx`
  - main workbench와 history가 같이 쓰는 공통 preview block 추가
- `apps/web/src/components/demo-workbench.tsx`
  - 기존 `scenePlan 확인` block을 공통 컴포넌트로 교체
- `apps/web/src/components/history-board.tsx`
  - 결과가 있는 경우 `scenePlan 미리보기` block 추가
  - 기본 선택 프로젝트를 `generated/upload_assist/publishing/published` 우선으로 조정
- `scripts/capture_history_scene_plan_preview.mjs`
  - `/history` 화면을 실제로 캡처해 preview block 노출 여부를 확인하는 스크립트 추가

## 5. 결과

### 생성 artifact

- `docs/experiments/artifacts/exp-22-history-scene-plan-preview/history-scene-plan.png`
- `docs/experiments/artifacts/exp-22-history-scene-plan-preview/summary.json`

### 확인된 것

1. `history` 화면에서도 opening/closing scene으로 바로 넘어가는 `scenePlan 미리보기` 링크가 표시됩니다.
2. 결과가 있는 프로젝트를 기본 선택으로 올리면서, 최초 진입 시에도 preview block이 바로 보입니다.
3. 이제 메인 화면과 이력 화면이 같은 result 확인 경로를 사용합니다.

## 6. 실패/제약

1. 최초 구현에서는 기본 선택 프로젝트가 `생성 중` 항목으로 잡혀 preview가 화면에 보이지 않았습니다.
2. 이 문제는 렌더 버그가 아니라 목록 선택 우선순위 문제였고, result-ready 상태 우선 선택으로 수정했습니다.
3. 이번 작업도 visual quality 개선이 아니라 `확인 surface 정렬` 작업입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 이제 `scenePlan` preview는 main workbench만의 기능이 아니라, history/result 화면에서도 일관되게 확인할 수 있습니다.
  - 이후 prompt/model 실험 결과도 두 화면 중 어느 쪽에서 보더라도 같은 기준으로 확인할 수 있습니다.

## 8. 다음 액션

1. 다음은 실제 생성 실험 결과를 `history`에서 바로 비교할 수 있는 최소 comparison view를 고민합니다.
2. 그 다음 prompt/model OVAT 실험을 다시 서비스 루프 기준으로 이어갑니다.

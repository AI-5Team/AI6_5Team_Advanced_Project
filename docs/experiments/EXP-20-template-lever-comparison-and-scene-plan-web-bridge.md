# EXP-20 Template Lever Comparison and Scene Plan Web Bridge

## 1. 기본 정보

- 실험 ID: `EXP-20`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: 템플릿별 상위 prompt lever 비교, `scenePlan -> web/capture` 연결

## 2. 왜 이 작업을 했는가

- `EXP-15`부터 `EXP-19`까지 돌려 보니 템플릿별로 잘 먹는 레버가 다르다는 점이 분명해졌습니다.
- 동시에 `scenePlan`이 worker/API까지는 연결됐지만, web surface는 아직 hardcoded scene에 크게 의존하고 있었습니다.
- 그래서 이번에는
  1. `promotion`과 `review`의 상위 레버를 비교 표로 정리하고
  2. 실제 prompt experiment artifact의 `scene_plan`을 `scene-frame`이 직접 읽어 PNG로 캡처되는지
  를 함께 검증했습니다.

## 3. 무엇을 바꿨는가

### web bridge

- `apps/web/src/lib/scene-plan.ts`
  - prompt experiment artifact catalog 추가
  - `scenePlan` loader 추가
- `apps/web/src/app/api/local-media/route.ts`
  - `/docs/sample/*`, `/samples/input/*` 로컬 이미지를 안전하게 서빙하는 route 추가
- `apps/web/src/components/scene-lab.tsx`
  - `scenePlan`을 `SceneSpec`으로 변환하는 mapper 추가
  - `/scene-lab`에 실제 artifact frame 링크 추가
- `apps/web/src/app/scene-frame/[scene]/page.tsx`
  - `?artifact=` query가 있으면 실제 `scenePlan` artifact를 읽어 렌더하도록 수정
- `scripts/capture_scene_plan_frames.mjs`
  - 실제 `scenePlan` 기반 scene-frame을 캡처하는 스크립트 추가

## 4. 템플릿별 비교 요약

| 템플릿 | 주요 실험 | 가장 유효했던 레버 | 이유 |
|---|---|---|---|
| `T02 promotion` | `EXP-15` | `B급 tone guidance` | 길이 예산을 지키면서 혜택/기간/CTA를 더 직접적으로 만들었습니다. |
| `T04 review` | `EXP-16`~`EXP-19` | `지역 반복 제약`, `CTA 강도` | `review`는 톤보다 정책 제약과 마지막 행동 문구가 더 큰 영향을 줬습니다. |

### promotion 측 판단

- 관련 실험: `EXP-15`
- winner:
  - `B급 tone guidance`
- 확인된 변화:
  - `오늘만 특가 할인!`
  - `재고 소진 시 종료!`
  - `지금 바로 예약!`
- 판단:
  - `promotion`은 장면 목적이 분명해서 톤 지시가 바로 장면 직접성으로 이어졌습니다.

### review 측 판단

- 관련 실험: `EXP-16`, `EXP-17`, `EXP-18`, `EXP-19`
- winner:
  - `지역 반복 제약`
  - `CTA 강도`
- 덜 효과적이었던 레버:
  - `B급 review tone guidance`
  - `slot 길이 제한` 단독
- 판단:
  - `review`는 과장 톤보다 `지역 반복 억제`, `저장/방문` 같은 마지막 행동 문구가 더 중요했습니다.

## 5. 실제 web bridge 검증

아래 4개 frame을 실제 `scenePlan` artifact에서 직접 읽어 캡처했습니다.

- `promotion-opening.png`
- `promotion-closing.png`
- `review-region-opening.png`
- `review-cta-closing.png`

artifact:

- `docs/experiments/artifacts/exp-20-scene-plan-web-bridge/promotion-opening.png`
- `docs/experiments/artifacts/exp-20-scene-plan-web-bridge/promotion-closing.png`
- `docs/experiments/artifacts/exp-20-scene-plan-web-bridge/review-region-opening.png`
- `docs/experiments/artifacts/exp-20-scene-plan-web-bridge/review-cta-closing.png`
- `docs/experiments/artifacts/exp-20-scene-plan-web-bridge/summary.json`

## 6. 관찰 내용

### 확인된 것

1. `scene-frame`이 hardcoded scene뿐 아니라 실제 prompt experiment artifact의 `scene_plan`도 직접 렌더할 수 있게 됐습니다.
2. `promotion`과 `review` 모두 실제 생성 카피를 web poster surface에서 바로 볼 수 있게 됐습니다.
3. 템플릿별 상위 레버 차이도 더 명확해졌습니다.
   - `promotion`: 톤
   - `review`: 제약 + CTA

### 아직 남은 것

1. 현재는 artifact 파일을 읽는 bridge입니다.
2. 아직 `/api/projects/{projectId}/result`의 `scenePlan` 링크를 web이 직접 소비하지는 않습니다.
3. 실제 서비스 루프 기준 마지막 연결은 “result API -> scene frame renderer”입니다.

## 7. 실패/제약

1. `capture_scene_plan_frames.mjs` 초안은 `next start` 작업 디렉터리와 workspace 명령 조합 때문에 한 번 실패했고 수정 후 재실행했습니다.
2. `scenePlan` bridge는 prompt experiment artifact 기준이라 production result API와는 아직 분리돼 있습니다.
3. 캡처 기준 surface는 현재 정적 poster frame이며, video composition까지 직접 연결한 상태는 아닙니다.

## 8. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 이제 “어떤 레버가 좋은가”를 말로만 정리한 게 아니라, 실제 `scenePlan` 결과를 web frame으로 바로 볼 수 있는 상태가 됐습니다.
  - 다음 단계는 prompt 레버 추가 실험이 아니라, 이 bridge를 production result API까지 연결하는 것입니다.

## 9. 다음 액션

1. web이 experiment artifact 대신 `/api/projects/{projectId}/result.scenePlan`을 직접 읽도록 연결합니다.
2. 그 다음 `scenePlan` 기반 capture를 worker run 단위로 재현합니다.

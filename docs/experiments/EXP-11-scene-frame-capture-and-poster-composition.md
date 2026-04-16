# EXP-11 Scene Frame Capture and Poster Composition

## 1. 기본 정보

- 실험 ID: `EXP-11`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: HTML/CSS scene frame, browser capture, poster-like composition

## 2. 왜 이 실험을 추가했는가

- `EXP-10`으로 `/scene-lab` 프로토타입은 만들었지만, 아직 결과물을 이미지 파일로 고정해서 비교할 수는 없었습니다.
- 사용자 피드백 기준으로는 “랩 페이지가 있다”보다 “실제로 덜 구린 frame이 뽑히는가”가 더 중요했습니다.
- 따라서 이번에는 HTML/CSS scene를 `독립 frame route`로 분리하고, `headless browser capture`까지 붙여 재현 가능한 산출물로 만들었습니다.

## 3. baseline

- 기준선: `EXP-10`의 `/scene-lab` prototype
- 한계:
  - preview page 중심이라 실제 frame capture 검증이 불가능했음
  - 장면 composition이 아직 카드형 preview 성격에서 완전히 벗어나지 못했음
  - Pillow 결과와 직접 비교 가능한 PNG artifact가 없었음

## 4. 이번 실험에서 바꾼 것

1. `apps/web/src/components/scene-lab.tsx`
   - scene definition을 shared component로 정리
   - 장면 composition을 `poster-like full-bleed frame` 기준으로 다시 작성
   - 억지 장식 문구 없이 `실사 사진 + 혜택 + CTA` 중심으로 정리
2. `apps/web/src/app/scene-frame/[scene]/page.tsx`
   - nav 없는 독립 frame route 추가
   - headless screenshot용 캡처 표면 분리
3. `apps/web/src/components/app-nav.tsx`
   - `/scene-frame/*`에서는 상단/하단 navigation을 숨기도록 수정
4. `scripts/capture_scene_lab_frames.mjs`
   - `npm run build:web`
   - `next start`
   - Chrome headless screenshot
   - artifact summary 저장
   를 한 번에 수행하는 재현 스크립트 추가

## 5. 결과

### 확인된 것

1. HTML/CSS scene를 실제 PNG artifact로 안정적으로 캡처할 수 있게 됐습니다.
2. opening scene은 기존 Pillow 결과보다 훨씬 덜 조악하고, 적어도 “실제 광고 컷”에 가까운 레이아웃으로 넘어가기 시작했습니다.
3. 캡처 artifact가 생기면서 이제부터는 감상평이 아니라 파일 비교 기반으로 방향을 논의할 수 있게 됐습니다.

### artifact

- `docs/experiments/artifacts/exp-11-html-css-scene-capture/scene-opening.png`
- `docs/experiments/artifacts/exp-11-html-css-scene-capture/scene-closing.png`
- `docs/experiments/artifacts/exp-11-html-css-scene-capture/summary.json`

## 6. 실패/제약

1. closing scene은 아직 typography polish가 부족합니다.
   - headline 밀도와 body copy 길이 제어가 더 필요합니다.
2. 현재는 web capture pipeline이며, worker의 실제 video render path와는 아직 분리돼 있습니다.
3. 장면 quality는 좋아졌지만, 아직 “제품 baseline 확정”이라고 부를 수준은 아닙니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `Pillow -> HTML/CSS` 전환은 맞는 방향입니다.
  - 다만 이제부터는 scene마다 copy 길이와 typography scale을 더 엄격하게 제한해야 합니다.
  - 다음 품질 병목은 모델보다 `scene copy budget + type system` 쪽입니다.

## 8. 다음 액션

1. opening / closing / review형 scene별 `copy budget`을 먼저 정합니다.
2. `scene-frame`을 기준으로 typography scale, line count, CTA placement를 다시 polish합니다.
3. 그 다음에야 `worker render pipeline`으로 이 경로를 이식할지 판단합니다.

# EXP-03 B급 영상 레이아웃 실험

## 1. 기본 정보

- 실험 ID: `EXP-03`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `b_grade_fun` 영상 렌더 표현, 전단지형 B급 화면 구성

## 2. 이번 실험 전에 명시한 기준선

- `B급 감성`은 이 프로젝트의 핵심 차별화 키워드로 둡니다.
- 실험 우선순위는 카피 미세조정보다 **영상 생성 연구**를 먼저 둡니다.
- 관련 기준선 변경은 `docs/adr/ADR-005-b-grade-video-first-experiment-priority.md`에 기록했습니다.

## 3. 실험 목적

- 현재 production 카드형 오버레이가 `b_grade_fun` 스타일에서도 충분히 B급스럽게 보이는지 검증합니다.
- 같은 카피, 같은 자산, 같은 템플릿에서 **오버레이 레이아웃 한 가지**만 바꿨을 때 화면 인상이 얼마나 달라지는지 확인합니다.

## 4. baseline 실험 조건 고정

| 항목 | 고정값 |
|---|---|
| 스타일 | `b_grade_fun` |
| 템플릿 | `T02` |
| 업종 맥락 | 카페 할인형 시나리오 |
| 자산 세트 | `samples/input/cafe/cafe-latte-01.png`, `samples/input/cafe/cafe-dessert-02.png` |
| primary/sub copy | 실험 harness 내부 고정 문구 사용 |
| 비교 대상 | current production `card_panel` vs experimental `flyer_poster` |
| 바뀐 레버 | `overlay_layout` 한 가지 |

### 고정 카피

1. `오늘만 텐션 폭발`
2. `딸기라떼 1+1`
3. `지금 안 오면 손해`
4. `성수동으로 바로 뛰어오세요`

## 5. 이번 실험에서 바꾼 것

- baseline:
  - 현재 production renderer가 쓰는 하단 카드형 패널
- variant:
  - 형광 전단지형 B급 레이아웃
  - 큰 헤드라인
  - 검정 외곽선 텍스트
  - 회전 스티커 2개
  - 추가 배지 3개
  - 형광 바 2개

## 6. 구현 위치

- 실험 harness:
  - `services/worker/experiments/video_harness.py`
- 실행 스크립트:
  - `scripts/run_video_experiment.py`
- 결과 artifact:
  - `docs/experiments/artifacts/exp-03-b-grade-video-layout-experiment/summary.json`
  - `docs/experiments/artifacts/exp-03-b-grade-video-layout-experiment/baseline_card_overlay/preview.mp4`
  - `docs/experiments/artifacts/exp-03-b-grade-video-layout-experiment/bgrade_flyer_overlay/preview.mp4`

## 7. 실험 절차

1. `b_grade_fun` + `T02` 조합으로 고정 시나리오를 만들었습니다.
2. baseline과 variant 모두 동일한 4개 scene copy를 사용했습니다.
3. baseline은 production `create_scene_image()`를 그대로 사용했습니다.
4. variant는 실험용 `create_flyer_scene_image()`로만 렌더했습니다.
5. 첫 씬 이미지를 직접 확인해 질적 차이를 비교했습니다.

## 8. 결과

### 정량 결과

| 케이스 | overlay mode | headline size | badge count | accent blocks | rotated elements | B급 signal score |
|---|---|---|---|---|---|---|
| baseline | `card_panel` | `58` | `1` | `2` | `0` | `38.6` |
| variant | `flyer_poster` | `84` | `3` | `6` | `2` | `137.8` |

### 질적 비교

| 항목 | baseline card panel | B급 flyer poster |
|---|---|---|
| 첫 인상 | 읽기 쉬움, 안전함 | 훨씬 강하고 시선 강탈 |
| B급 신호 | 약함 | 강함 |
| 형광/전단지 느낌 | 제한적 | 명확함 |
| 상품 가시성 | 상대적으로 유지 | 헤드라인이 상품 일부를 덮음 |
| 정보 밀도 | 낮음 | 높음 |

### 실제 관찰

- baseline 첫 씬:
  - `docs/experiments/artifacts/exp-03-b-grade-video-layout-experiment/baseline_card_overlay/scenes/s1.png`
- variant 첫 씬:
  - `docs/experiments/artifacts/exp-03-b-grade-video-layout-experiment/bgrade_flyer_overlay/scenes/s1.png`

## 9. 중요한 발견

### 1. 현재 production baseline은 B급 감성이 약합니다

- `b_grade_fun` 색상은 써도 레이아웃은 여전히 정돈된 카드형이라, 첫 인상이 충분히 과장되지 않습니다.
- 즉, 지금 병목은 카피보다 **화면 구성**에 더 가깝습니다.

### 2. 전단지형 variant는 B급 신호를 확실히 올렸습니다

- 큰 헤드라인, 형광 바, 회전 스티커, 검정 외곽선이 첫 1초 인상을 크게 바꿨습니다.
- 사용자가 말한 `B급 감성` 방향에는 variant가 baseline보다 훨씬 가깝습니다.

### 3. 하지만 과해지면 상품 가시성을 해칩니다

- variant는 헤드라인이 커서 제품 영역 일부를 먹습니다.
- 이 상태로는 “재미있음”은 올라도 “무엇을 파는지”가 약해질 수 있습니다.

### 4. 영상 실험 중 baseline 버그를 하나 발견했습니다

- `load_font(..., bold=True)`가 `Arial`을 먼저 잡아 한국어 굵은 자막이 네모 상자로 깨질 수 있었습니다.
- `services/worker/utils/runtime.py`에서 bold font 우선순위를 `malgunbd -> malgun -> arial`로 수정했습니다.

## 10. 실패/제약

1. 이번 실험은 layout 비교라 motion 차이는 아직 검증하지 않았습니다.
2. `B급 signal score`는 실험용 heuristic이라 사람 평가를 대체하지는 않습니다.
3. variant는 일부 장면에서 텍스트 점유율이 높아 안전영역/상품 가시성 추가 검토가 필요합니다.
4. 아직 실제 매장 사진이 아니라 샘플 자산 기준입니다.

## 11. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `overlay_layout`은 B급 영상 인상에 매우 큰 레버입니다.
  - 이 프로젝트에서 영상 연구를 먼저 해야 한다는 판단이 강화됐습니다.
  - 다만 다음 단계는 “더 세게”가 아니라 “세지만 상품은 가리지 않게” 다듬는 방향이어야 합니다.

## 12. 다음 액션

1. 다음 영상 레버는 `headline occupancy` 또는 `상품 가시성 보호 영역`으로 잡습니다.
2. `flyer_poster` 계열을 유지하되, 헤드라인 높이와 위치만 줄여 one-variable-at-a-time으로 다시 비교합니다.
3. 이후에야 `motion preset`(shake/flash/zoom) 실험으로 넘어갑니다.

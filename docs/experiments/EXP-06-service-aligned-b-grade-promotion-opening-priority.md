# EXP-06 서비스 기준선 정렬 B급 프로모션 첫 씬 우선순위 실험

## 1. 기본 정보

- 실험 ID: `EXP-06`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `promotion` 템플릿 첫 씬 메시지 우선순위, 서비스 루프 기준 B급 숏폼 실험

## 2. 왜 이 실험을 추가했는가

- 기획 문서를 다시 확인한 결과, 이 서비스의 핵심은 “B급 스타일 탐색” 자체가 아니라 **선택형 생성 -> 결과 확인 -> 빠른 수정 -> 업로드/업로드 보조** 루프입니다.
- 따라서 영상 실험도 서비스 핵심 경로에 맞춰야 합니다.
- `promotion` 목적에서는 `혜택 + 기간감 + CTA` 구조가 명시되어 있으므로, 첫 씬을 `혜택 우선`으로 열지 `메뉴 우선`으로 열지 먼저 확인할 필요가 있습니다.

## 3. baseline 실험 조건 고정

| 항목 | 고정값 |
|---|---|
| 업종 | `restaurant` |
| 목적 | `promotion` |
| 스타일 | `b_grade_fun` |
| 템플릿 | `T02` |
| 채널 관점 | `instagram` 업로드 가능 결과물 기준 |
| 자산 세트 | `docs/sample/음식사진샘플(규카츠).jpg`, `docs/sample/음식사진샘플(맥주).jpg` |
| 오버레이 레이아웃 | `owner_made_safe` |
| 바뀐 레버 | `opening_scene_priority` 한 가지 |

## 4. 이번 실험에서 바꾼 것

- baseline
  - `owner_made_benefit_first`
  - 첫 씬 primary: `오늘만 2천원↓`
  - 첫 씬 secondary: `규카츠 세트 특가`
- variant
  - `owner_made_menu_first`
  - 첫 씬 primary: `겉바 규카츠`
  - 첫 씬 secondary: `오늘만 2천원↓ / 세트 특가`

즉, 같은 자산, 같은 레이아웃, 같은 씬 수, 같은 CTA 조건에서 **첫 씬의 정보 우선순위만 바꿨습니다.**

## 5. 실험 절차

1. planning 문서를 다시 읽고 서비스 루프 기준선을 재정리했습니다.
2. `video_harness.py`에 `EXP-06`과 `scene_text_overrides`를 추가했습니다.
3. 실험용 baseline을 `restaurant / promotion / b_grade_fun / T02`로 고정했습니다.
4. `uv run --project services/worker python scripts/run_video_experiment.py --experiment-id EXP-06`를 실행했습니다.
5. baseline/variant의 첫 씬 이미지를 직접 비교했습니다.

## 6. 결과

### artifact

- `docs/experiments/artifacts/exp-06-service-aligned-b-grade-promotion-opening-priority/summary.json`

### 정량 결과

| 케이스 | opening focus | promotion score | menu clarity | service-loop fit |
|---|---|---|---|---|
| baseline | `benefit_first` | `100.0` | `68.0` | `88.8` |
| variant | `menu_first` | `68.0` | `100.0` | `82.4` |

### 질적 비교

| 항목 | benefit first | menu first |
|---|---|---|
| 첫 1초 메시지 | “할인/특가”가 바로 읽힘 | 메뉴명 인지는 빠름 |
| promotion 목적 적합성 | 높음 | 중간 |
| 상품 정보 인지 | 중간 | 높음 |
| CTA로 이어지는 흐름 | 더 자연스러움 | 첫 씬에서 프로모션 목적이 약해짐 |

## 7. 관찰 내용

### 확인된 것

1. `promotion` 목적의 T02에서는 첫 씬을 혜택 우선으로 여는 편이 서비스 문서의 목적 구조와 더 잘 맞았습니다.
2. 메뉴 우선 variant는 음식 이름 인지는 빨랐지만, “할인/행사” 목적이 첫 1초 안에 덜 드러났습니다.
3. 즉 이 서비스의 B급 숏폼은 무조건 메뉴를 먼저 보여주는 것보다, **목적에 맞는 정보 우선순위**를 먼저 맞추는 편이 더 중요합니다.

### 이번 실험에서 서비스 이해 관점으로 확인된 것

1. 실험 단위는 스타일 장식보다 `목적 구조를 잘 전달하는가`로 잡는 편이 더 맞습니다.
2. B급 감성도 결국 `promotion`, `review` 같은 서비스 목적 안에서 작동해야 합니다.
3. quick action 실험도 앞으로는 이 기준을 따라야 합니다.

## 8. 실패/제약

1. `owner_made_safe` 오버레이는 긴 프로모션 헤드라인이 오른쪽 경계에서 잘리는 제약이 있어, 첫 실행 뒤 더 짧은 문구로 다시 맞췄습니다.
2. 현재 점수는 heuristic 기반이라 사람 평가를 완전히 대체하지는 못합니다.
3. 아직 영상 모션이 아니라 정적 씬 우선순위만 비교한 상태입니다.

## 9. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 서비스 기준선으로 보면 `benefit_first`가 더 적합합니다.
  - `menu_first`는 메뉴 전달은 좋지만 `promotion` 목적 설명력이 약해집니다.
  - 다음 실험도 같은 baseline에서 `subtitle_density`나 `quick action delta`를 보는 편이 맞습니다.

## 10. 다음 액션

1. 다음 레버는 `subtitle_density`로 잡습니다.
   - baseline: 메인 + 보조 문구
   - variant: 메인 문구만
2. `owner_made_safe`의 우측 텍스트 overflow는 별도 레이아웃 개선 실험으로 분리합니다.
3. 같은 서비스 baseline에서 quick action `문구 더 짧게`가 실제로 눈에 띄는지 이어서 확인합니다.

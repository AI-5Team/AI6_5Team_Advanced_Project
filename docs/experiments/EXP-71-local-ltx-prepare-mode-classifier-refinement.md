# EXP-71 Local LTX prepare_mode classifier refinement

## 1. 기본 정보

- 실험 ID: `EXP-71`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / prepare_mode auto classifier v2`

## 2. 왜 이 작업을 했는가

- `EXP-69`의 auto classifier v1은 known baseline 6장에는 맞았지만, `맥주`를 `contain_blur`로 예측했습니다.
- 그런데 `EXP-70`에서 실제 생성 비교 결과 `맥주`도 `cover_top`이 더 좋았습니다.
- 따라서 이번에는 auto classifier를 `drink top-bias` evidence에 맞게 보정하고, v1 대비 실제 정확도가 올라가는지 확인했습니다.

## 3. baseline

### 고정한 조건

1. 평가 이미지: `docs/sample`의 음식 사진 전부
2. known policy labels:
   - `규카츠`: `cover_center`
   - `라멘`: `contain_blur`
   - `순두부짬뽕`: `contain_blur`
   - `장어덮밥`: `contain_blur`
   - `커피`: `cover_top`
   - `맥주`: `cover_top`
   - `아이스크림`: `contain_blur`

### 이번에 바꾼 레버

- `classifier rule`만 바꿨습니다.
- baseline: v1
  - `top_edge_ratio` 중심 drink detection
- variant: v2
  - `bottom_edge_ratio`와 `center_edge_ratio`를 추가해 `맥주` 같은 bottle/glass shot도 `glass_drink_candidate`로 포착

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_prepare_mode_classifier.py`
   - drink candidate 조건에 `bottom-heavy portrait drink` 패턴을 추가했습니다.
2. `scripts/local_video_ltx_prepare_mode_classifier_refinement.py`
   - v1과 v2를 나란히 비교하고 known baseline 정확도를 계산하는 스크립트를 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-71-local-ltx-prepare-mode-classifier-refinement/summary.json`

### aggregate

- changed count: `1`
- changed label: `맥주`

### known baseline 정확도

- known eval image count: `7`
- v1 accuracy: `0.8571`
- v2 accuracy: `1.0`

### 확인된 것

1. v2에서 바뀐 샘플은 `맥주` 1장뿐이었습니다.
2. 그 변경이 실제 `EXP-70` 결과와 일치합니다.
3. 즉 v2는 기존 known baseline을 유지하면서 `맥주` 오분류만 바로잡았습니다.

## 6. 실패/제약

1. 현재 classifier는 여전히 작은 샘플셋에 맞춘 heuristic입니다.
2. `glass drink candidate`를 더 넓은 음료 사진군에 적용해도 유지되는지는 아직 모릅니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - current research baseline에서는 auto classifier v2를 쓰는 편이 맞습니다.
  - 지금까지의 결과를 종합하면 `prepare_mode`는 아래 정책으로 좁혀졌습니다.
    - `tray/full-plate -> cover_center`
    - `glass drink candidate -> cover_top`
    - 그 외 preserve-shot -> `contain_blur`

## 8. 다음 액션

1. 다음은 이 v2 policy를 실제 LTX batch runner나 후속 generation harness에 반영하는 것입니다.
2. 추가 샘플이 생기면 먼저 `glass drink candidate` 일반화부터 다시 확인합니다.

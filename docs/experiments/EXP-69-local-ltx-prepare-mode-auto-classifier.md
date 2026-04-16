# EXP-69 Local LTX prepare_mode auto classifier

## 1. 기본 정보

- 실험 ID: `EXP-69`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / image-only prepare_mode 자동 분기`

## 2. 왜 이 작업을 했는가

- `EXP-66`부터 `EXP-68`까지의 결과로, 현재 single-photo baseline은 prompt보다 `prepare_mode policy`가 더 큰 레버라는 점이 확인됐습니다.
- 다만 그 정책을 파일명이나 수동 규칙으로만 유지하면 실제 서비스 경로로 옮기기 어렵습니다.
- 그래서 이번에는 이미지 구조 feature만 보고 `prepare_mode`를 고르는 간단한 auto classifier가 현재 baseline policy를 얼마나 재현하는지 확인했습니다.

## 3. baseline

### 고정한 조건

1. 입력 자산: `docs/sample`의 음식 사진 전부
2. known baseline policy:
   - `규카츠`: `cover_center`
   - `라멘`: `contain_blur`
   - `순두부짬뽕`: `contain_blur`
   - `장어덮밥`: `contain_blur`
   - `커피`: `cover_top`
   - `아이스크림`: `contain_blur`

### 이번에 바꾼 레버

- `prepare_mode selection method`만 바꿨습니다.
- baseline: 수동으로 정한 known policy
- variant: 이미지 구조 feature 기반 auto classifier

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_prepare_mode_classifier.py`
   - 이미지 구조 feature 추출
   - `tray_full_plate / glass_drink_candidate / preserve_shot` 분류
   - `prepare_mode` 선택 로직 추가
2. `scripts/local_video_ltx_prepare_mode_auto_classifier.py`
   - 전체 샘플 이미지에 대해 auto classifier 결과와 known baseline 일치도를 요약하도록 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-69-local-ltx-prepare-mode-auto-classifier/summary.json`

### known baseline 일치도

- known baseline 평가 대상: `6장`
- matched count: `6`
- accuracy: `1.0`

### 추가 예측

1. `맥주`
   - auto classifier v1 예측: `contain_blur`
2. `타코야키`
   - auto classifier v1 예측: `cover_center`
3. `귤모찌`, `초코소보로호두과자`, `카오위`
   - auto classifier v1 예측: `contain_blur`

### 확인된 것

1. 현재 known baseline 6장에 대해서는 image-only classifier가 수동 정책을 재현했습니다.
2. 즉 `prepare_mode`는 파일명 하드코딩 없이도 간단한 feature로 일정 수준 자동화할 수 있습니다.
3. 다만 `맥주`처럼 아직 생성 실험으로 검증되지 않은 샘플은 추가 확인이 필요합니다.

## 6. 실패/제약

1. 이번 실험은 classification-only라 실제 비디오 품질 차이를 직접 검증하지 않았습니다.
2. `맥주` 예측은 아직 hypothesis 단계였습니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - auto classifier v1은 known set에서는 충분히 맞았습니다.
  - 다만 `맥주` 같은 새 drink 사진에 대해서는 실제 생성 비교가 필요합니다.

## 8. 다음 액션

1. 다음은 `맥주`를 포함한 drink subset에서 `contain_blur vs cover_top`을 직접 비교합니다.
2. 그 결과에 따라 auto classifier를 보정할지 결정합니다.

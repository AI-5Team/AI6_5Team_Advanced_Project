# EXP-84 Local LTX beer cover bottom bias OVAT

## 1. 기본 정보

- 실험 ID: `EXP-84`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / beer lane framing follow-up`

## 2. 왜 이 작업을 했는가

- `EXP-83`에서 `맥주`는 `cover_top`보다 `cover_center`가 더 좋았습니다.
- 하지만 원본 이미지를 보면 bottle label과 glass 하단 정보가 여전히 프레임 아래쪽에 몰려 있어, `cover_center`보다 더 낮은 bias가 유효할 가능성이 있었습니다.
- 그래서 이번에는 baseline을 `cover_center`로 고정하고, `cover_bottom` 편향만 추가하는 OVAT를 진행했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. 이미지: `맥주`
4. prompt:
   - `beer bottle and lager glass, bright tabletop lighting, still life beverage shot, static close-up, minimal camera movement`
5. negative prompt: 기본값
6. frames / steps / fps: `25 / 6 / 8`

### 이번에 바꾼 레버

- `prepare_mode`만 바꿨습니다.
- baseline:
  - `cover_center`
- variant:
  - `cover_bottom`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_first_try.py`
   - 실험용으로 `cover_bottom` prepare mode를 추가했습니다.
2. `scripts/local_video_ltx_beer_cover_bottom_bias_ovaat.py`
   - `cover_center`와 `cover_bottom`을 비교하는 OVAT 스크립트를 추가했습니다.
3. `scripts/local_video_ltx_prepare_mode_classifier.py`
   - `bottom-heavy bottle+glass` 케이스를 `cover_bottom`으로 분기하도록 다시 보정했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-84-local-ltx-beer-cover-bottom-bias-ovaat/summary.json`

### aggregate

- baseline mid-frame MSE: `120.99`
- variant mid-frame MSE: `103.34`
- mid-frame MSE delta: `+17.65`
- edge variance delta: `+60.50`

### 확인된 것

1. `cover_bottom`이 `cover_center`보다 소폭 더 좋았습니다.
2. prepared input 단계에서도 label 하단과 glass 영역이 더 넓게 살아났습니다.
3. 즉 `맥주`처럼 하단 정보가 큰 bottle+glass shot은 `cover_center`보다 `cover_bottom`이 더 잘 맞습니다.

## 6. 실패/제약

1. 개선 폭은 `EXP-83`보다 작습니다.
2. 근거는 아직 `맥주` 1장뿐입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 현재 bottom-heavy bottle+glass baseline은 `cover_center`보다 `cover_bottom`이 더 적절합니다.
  - drink lane prepare-mode 분기는 `top-heavy -> cover_top`, `bottom-heavy bottle+glass -> cover_bottom`으로 정리하는 편이 맞습니다.

## 8. 다음 액션

1. 다음은 classifier 보정 후에도 `커피`는 `cover_top`, `맥주`는 `cover_bottom`이 유지되는지 확인합니다.
2. 새 bottle+glass 실사 샘플이 생기면 같은 분기가 유지되는지 다시 검증해야 합니다.

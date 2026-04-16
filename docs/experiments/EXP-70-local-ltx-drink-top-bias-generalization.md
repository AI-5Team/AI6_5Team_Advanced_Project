# EXP-70 Local LTX drink top bias generalization

## 1. 기본 정보

- 실험 ID: `EXP-70`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / drink subset prepare_mode generalization`

## 2. 왜 이 작업을 했는가

- `EXP-67`에서 `커피`는 `cover_top`이 더 좋았지만, 그때는 drink 샘플이 1장뿐이었습니다.
- 그런데 `docs/sample` 안에 `맥주` 사진도 있어, `cover_top`이 커피 전용 예외인지 drink 일반 규칙 후보인지 볼 수 있게 됐습니다.
- 이번에는 drink subset에서 `prepare_mode`만 바꿔 `cover_top`이 실제로 일반화되는지 확인했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. prompt:
   - `커피`: `iced coffee, bright tabletop lighting, realistic drink commercial motion, static close-up, minimal camera movement`
   - `맥주`: `beer bottle and lager glass, bright tabletop lighting, realistic drink commercial motion, static close-up, minimal camera movement`
4. negative prompt: 기본값
5. frames / steps / fps: `25 / 6 / 8`
6. 이미지:
   - `커피`
   - `맥주`

### 이번에 바꾼 레버

- `prepare_mode`만 바꿨습니다.
- baseline: `contain_blur`
- variant: `cover_top`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_drink_top_bias_generalization.py`
   - drink subset에 대해 `contain_blur`와 `cover_top`만 비교하도록 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-70-local-ltx-drink-top-bias-generalization/summary.json`

### 이미지별 결과

1. 커피
   - `cover_top`이 더 좋았습니다.
   - mid-frame MSE delta: `+291.31`
2. 맥주
   - `cover_top`이 더 좋았습니다.
   - mid-frame MSE delta: `+340.30`

### aggregate

- `cover_top`이 더 나은 이미지는 `2개 중 2개`였습니다.
- average mid-frame MSE delta는 `+315.81`이었습니다.
- average edge variance delta는 `+182.52`였습니다.

### 확인된 것

1. `cover_top`은 `커피` 한 장만의 예외가 아니었습니다.
2. `맥주`까지 포함한 drink subset에서도 `cover_top`이 `contain_blur`보다 더 좋았습니다.
3. 따라서 현재 baseline은 `glass drink candidate -> cover_top`로 일반화할 근거가 생겼습니다.

## 6. 실패/제약

1. drink subset이 아직 `커피`, `맥주` 2장뿐입니다.
2. prompt를 drink 전용으로 다시 맞췄기 때문에 이전 coffee 실험과 수치가 직접 1:1 대응되지는 않습니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `cover_top`은 drink candidate의 일반 규칙 후보가 됐습니다.
  - auto classifier가 `맥주`를 `contain_blur`로 본 v1은 보정이 필요합니다.

## 8. 다음 액션

1. auto classifier에 `맥주` 케이스를 반영한 v2를 만듭니다.
2. v1과 v2를 비교해 known baseline 정확도가 실제로 올라가는지 확인합니다.

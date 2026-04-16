# EXP-78 Local LTX beer drink motion phrase OVAT

## 1. 기본 정보

- 실험 ID: `EXP-78`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / drink lane 후속 레버`

## 2. 왜 이 작업을 했는가

- `prepare_mode auto` 기준으로 `맥주`는 `glass_drink_candidate -> cover_top`으로 올바르게 분기됐지만, `커피`보다 mid-frame 품질이 훨씬 거칠었습니다.
- 원본 이미지를 보면 `맥주`는 bottle + glass + foam 조합이라 liquid/reflection 해석이 흔들릴 가능성이 높았습니다.
- 그래서 이번에는 drink lane에서 `motion/style phrase` 하나만 바꿔, `realistic drink commercial motion` 대신 더 정적인 `still life beverage shot`이 나은지 확인했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. 이미지: `맥주`
4. prepare mode: `auto` (`resolved_prepare_mode = cover_top`)
5. negative prompt: 기본값
6. frames / steps / fps: `25 / 6 / 8`

### 이번에 바꾼 레버

- `drink motion phrase`만 바꿨습니다.
- baseline:
  - `beer bottle and lager glass, bright tabletop lighting, realistic drink commercial motion, static close-up, minimal camera movement`
- variant:
  - `beer bottle and lager glass, bright tabletop lighting, still life beverage shot, static close-up, minimal camera movement`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_beer_drink_motion_phrase_ovaat.py`
   - `맥주` 1장에서 baseline motion phrase와 still-life variant를 비교하는 OVAT 스크립트를 추가했습니다.
2. `scripts/local_video_ltx_batch_runner.py`
   - reusable runner에서 `맥주` prompt만 `still life beverage shot` 예외를 쓰도록 수정했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-78-local-ltx-beer-drink-motion-phrase-ovaat/summary.json`

### aggregate

- baseline mid-frame MSE: `797.78`
- variant mid-frame MSE: `268.79`
- mid-frame MSE delta: `+528.99`
- edge variance delta: `+50.08`

### 확인된 것

1. `still life beverage shot` variant가 수치상 크게 더 좋았습니다.
2. 실제 mid frame에서도 baseline보다 glass foam과 bottle 주변 흔들림이 줄었습니다.
3. 따라서 현재 `맥주` 병목은 prepare mode가 아니라 `drink commercial motion` 해석 쪽이 더 컸습니다.

## 6. 실패/제약

1. 이번 결과는 `맥주` 1장 기준입니다.
2. `still life beverage shot`를 drink lane 전체 기본값으로 올릴 근거는 아직 부족합니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `맥주`는 drink lane 안에서도 `커피`와 같은 prompt family로 처리하기보다 별도 예외로 보는 편이 맞습니다.
  - 현재 baseline에서는 `맥주 = cover_top + still life beverage shot`이 더 적절합니다.

## 8. 다음 액션

1. 다음은 `커피`에도 같은 레버를 붙였을 때 유지되는지 보거나,
2. `맥주`의 다음 병목인 bottle label / glass foam 보존을 위한 후속 레버를 따로 보는 편이 맞습니다.

# EXP-80 Local LTX beer carbonation phrase OVAT

## 1. 기본 정보

- 실험 ID: `EXP-80`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / beer lane 후속 레버`

## 2. 왜 이 작업을 했는가

- `EXP-78`과 `EXP-79`를 통해 drink lane 기본값은 `still life beverage shot`로 좁혀졌습니다.
- 그 다음 `맥주`에서 남은 병목은 bottle label과 foam/carbonation 보존으로 보였습니다.
- 그래서 이번에는 `맥주` baseline을 고정하고, `subtle carbonation bubbles, crisp foam rim`만 추가하는 OVAT를 진행했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. 이미지: `맥주`
4. prepare mode: `auto` (`resolved_prepare_mode = cover_top`)
5. negative prompt: 기본값
6. frames / steps / fps: `25 / 6 / 8`

### 이번에 바꾼 레버

- `carbonation/foam phrase`만 바꿨습니다.
- baseline:
  - `beer bottle and lager glass, bright tabletop lighting, still life beverage shot, static close-up, minimal camera movement`
- variant:
  - `beer bottle and lager glass, bright tabletop lighting, still life beverage shot, subtle carbonation bubbles, crisp foam rim, static close-up, minimal camera movement`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_beer_carbonation_phrase_ovaat.py`
   - `맥주` 1장에서 carbonation/foam phrase를 추가한 variant를 baseline과 비교하도록 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-80-local-ltx-beer-carbonation-phrase-ovaat/summary.json`

### aggregate

- baseline mid-frame MSE: `268.79`
- variant mid-frame MSE: `187.23`
- mid-frame MSE delta: `+81.56`
- edge variance delta: `-11.39`

### 확인된 것

1. 수치상으로는 carbonation/foam phrase variant가 더 좋았습니다.
2. 시각적으로도 foam 쪽 밀도는 약간 더 좋아졌습니다.
3. 다만 edge variance는 소폭 내려가서, 무조건 baseline으로 승격할 만큼 일방적인 결과는 아니었습니다.

## 6. 실패/제약

1. `맥주` 1장 기준입니다.
2. `edge variance`가 약간 낮아져, label/foam 보존이 전반적으로 더 좋아졌다고 단정하기 어렵습니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `carbonation/foam phrase`는 유망한 `맥주 전용` 후보입니다.
  - 하지만 아직 reusable runner baseline까지 올리기보다는 추가 샘플이나 후속 검증이 더 필요합니다.

## 8. 다음 액션

1. 새 drink 샘플이 생기면 `still life beverage shot` baseline 유지 여부를 먼저 다시 확인합니다.
2. `맥주`는 carbonation phrase보다 `label/text preservation` 쪽 레버가 더 큰지 후속 확인이 필요합니다.

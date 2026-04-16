# EXP-81 Local LTX beer label preservation phrase OVAT

## 1. 기본 정보

- 실험 ID: `EXP-81`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / beer lane 후속 레버`

## 2. 왜 이 작업을 했는가

- `EXP-80`까지의 결과로 `맥주`는 `cover_top + still life beverage shot`까지는 정리됐지만, bottle label과 글자 형태 보존은 여전히 약했습니다.
- 그래서 이번에는 baseline을 고정하고 `clear bottle label, readable paper label shape` phrase만 추가해서 label 보존이 실제로 개선되는지 확인했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. 이미지: `맥주`
4. prepare mode: `auto` (`resolved_prepare_mode = cover_top`)
5. negative prompt: 기본값
6. frames / steps / fps: `25 / 6 / 8`

### 이번에 바꾼 레버

- `label preservation phrase`만 바꿨습니다.
- baseline:
  - `beer bottle and lager glass, bright tabletop lighting, still life beverage shot, static close-up, minimal camera movement`
- variant:
  - `beer bottle and lager glass, bright tabletop lighting, still life beverage shot, clear bottle label, readable paper label shape, static close-up, minimal camera movement`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_beer_label_preservation_phrase_ovaat.py`
   - `맥주` baseline과 label-preservation phrase variant를 비교하는 OVAT 스크립트를 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-81-local-ltx-beer-label-preservation-phrase-ovaat/summary.json`

### aggregate

- baseline mid-frame MSE: `268.79`
- variant mid-frame MSE: `198.48`
- mid-frame MSE delta: `+70.31`
- edge variance delta: `-27.57`

### 확인된 것

1. 수치상으로는 `mid-frame MSE`가 좋아졌습니다.
2. 하지만 `edge variance`는 내려갔고, 실제 frame에서도 bottle label 글자가 명확하게 더 좋아졌다고 보긴 어려웠습니다.
3. 따라서 `label preservation phrase`는 완전 실패는 아니지만, baseline 승격 레버로 보기엔 근거가 약합니다.

## 6. 실패/제약

1. `맥주` 1장 기준입니다.
2. label 자체가 text fidelity 문제라, 일반 prompt phrase만으로는 개선 폭이 제한적일 수 있습니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `label preservation phrase`는 유망 후보로는 남길 수 있습니다.
  - 하지만 현재 baseline에는 반영하지 않고 보류하는 편이 맞습니다.

## 8. 다음 액션

1. 다음은 `negative prompt` 쪽이 label 보존에 영향을 주는지 따로 봅니다.
2. prompt보다 이미지 전처리나 crop 전략이 더 큰 레버인지도 검토할 필요가 있습니다.

# EXP-74 Local LTX takoyaki steam phrase OVAT

## 1. 기본 정보

- 실험 ID: `EXP-74`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / tray-full-plate 후속 레버`

## 2. 왜 이 작업을 했는가

- `EXP-73`에서 `prepare_mode auto`는 batch path에서도 유지됐지만, `타코야키`는 `tray_full_plate -> cover_center`로 올바르게 분기됐음에도 mid-frame 품질이 거칠었습니다.
- 따라서 다음 병목은 prepare_mode가 아니라 tray/full-plate용 prompt 안의 세부 문구라고 보고, 가장 의심스러운 `strong steam cloud`만 제거하는 OVAT를 진행했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. 이미지: `타코야키`
4. prepare mode: `auto` (`resolved_prepare_mode = cover_center`)
5. negative prompt: 기본값
6. frames / steps / fps: `25 / 6 / 8`

### 이번에 바꾼 레버

- `steam phrase`만 바꿨습니다.
- baseline:
  - `takoyaki snack tray, bright tabletop lighting, strong steam cloud, realistic food motion, static close-up, minimal camera movement`
- variant:
  - `takoyaki snack tray, bright tabletop lighting, realistic food motion, static close-up, minimal camera movement`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_takoyaki_steam_phrase_ovaat.py`
   - `strong steam cloud`가 있는 baseline과, 그 문구만 제거한 variant를 비교하도록 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-74-local-ltx-takoyaki-steam-phrase-ovaat/summary.json`

### aggregate

- mid-frame MSE delta: `+873.36`
- edge variance delta: `+375.32`

### 확인된 것

1. `strong steam cloud`를 제거한 variant가 수치상 크게 더 좋았습니다.
2. 실제 mid frame에서도 baseline보다 tray와 타코야키 경계가 더 안정적이었습니다.
3. 즉 `타코야키` 같은 tray snack 샘플에서는 `steam phrase`가 품질을 해치는 레버였습니다.

## 6. 실패/제약

1. 이번 결과는 `타코야키` 1장 기준입니다.
2. `steam phrase 제거`가 tray/full-plate 전반에 일반화되는지는 아직 모릅니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 현재 tray/full-plate 샷에서도 `steam phrase`는 기본값이 아니라 선택 옵션으로 봐야 합니다.
  - 특히 snack/tray 계열에는 `no steam` prompt family를 따로 두는 편이 맞습니다.

## 8. 다음 액션

1. 다음은 `tray/full-plate` 내부에서 `steam on/off`를 더 넓은 샘플에 다시 확인하는 것입니다.
2. 특히 `규카츠`와 `타코야키`를 나란히 두고 tray subtype 분기를 볼 수 있습니다.

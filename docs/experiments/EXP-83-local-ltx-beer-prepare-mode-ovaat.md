# EXP-83 Local LTX beer prepare mode OVAT

## 1. 기본 정보

- 실험 ID: `EXP-83`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / beer lane framing follow-up`

## 2. 왜 이 작업을 했는가

- `맥주`는 drink lane baseline인 `still life beverage shot`까지 정리됐지만, bottle label과 glass 하단 정보가 여전히 약했습니다.
- 앞선 prompt/negative prompt 실험 결과를 보면, 이제 남은 유력 레버는 `framing/crop` 쪽이었습니다.
- 그래서 이번에는 prompt는 고정하고 `prepare_mode`만 `cover_top -> cover_center`로 바꾸는 OVAT를 진행했습니다.

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
  - `cover_top`
- variant:
  - `cover_center`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_beer_prepare_mode_ovaat.py`
   - `cover_top`과 `cover_center`를 같은 prompt로 비교하는 OVAT 스크립트를 추가했습니다.
2. `scripts/local_video_ltx_prepare_mode_classifier.py`
   - `glass_drink_candidate` 중에서도 `bottom-heavy bottle+glass` 케이스는 `cover_center`로 분기하도록 보정했습니다.
   - 현재 기준으로 `맥주`는 이 분기에 걸리고, `커피`는 기존처럼 `cover_top`에 남습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-83-local-ltx-beer-prepare-mode-ovaat/summary.json`

### aggregate

- baseline mid-frame MSE: `268.79`
- variant mid-frame MSE: `120.99`
- mid-frame MSE delta: `+147.80`
- edge variance delta: `+226.31`

### 확인된 것

1. `cover_center`가 `cover_top`보다 명확히 더 좋았습니다.
2. prepared input 단계에서도 bottle label과 glass 하단 정보가 더 크게 살아났습니다.
3. 따라서 `맥주` 병목은 prompt보다 `prepare_mode` 쪽이 더 강했습니다.

## 6. 실패/제약

1. `맥주` 1장 기준입니다.
2. 현재 classifier 보정은 `coffee / beer` 두 샘플 차이에 근거한 보수적 분기입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `맥주`처럼 하단 정보 비중이 큰 bottle+glass shot은 `cover_top`보다 `cover_center`가 맞습니다.
  - 현재 baseline은 `glass_drink_candidate = cover_top` 단일 규칙이 아니라, `top-heavy -> cover_top`, `bottom-heavy bottle+glass -> cover_center`로 보는 편이 맞습니다.

## 8. 다음 액션

1. 다음은 classifier 보정이 `커피`는 그대로 `cover_top`, `맥주`는 `cover_center`를 유지하는지 확인합니다.
2. 그 이후에야 drink lane에서 새 샘플이 생길 때 이 분기가 일반화되는지 다시 검증할 수 있습니다.

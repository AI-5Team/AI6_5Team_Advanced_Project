# EXP-86 Local LTX beer glass separation phrase OVAT

## 1. 기본 정보

- 실험 ID: `EXP-86`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / beer lane 후속 레버`

## 2. 왜 이 작업을 했는가

- `EXP-84`까지의 결과로 `맥주` baseline은 `cover_bottom + still life beverage shot`로 좁혀졌습니다.
- 남은 가설은 bottle과 glass의 분리를 더 직접적으로 지시하면 흔들림이 줄어드는가였습니다.
- 그래서 이번에는 baseline을 고정하고 `clear separation between bottle and glass, distinct gap`만 추가하는 OVAT를 진행했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. 이미지: `맥주`
4. prepare mode: `cover_bottom`
5. prompt family:
   - `still life beverage shot`
6. negative prompt: 기본값
7. frames / steps / fps: `25 / 6 / 8`

### 이번에 바꾼 레버

- `glass separation phrase`만 바꿨습니다.
- baseline:
  - `beer bottle and lager glass, bright tabletop lighting, still life beverage shot, static close-up, minimal camera movement`
- variant:
  - `beer bottle and lager glass, bright tabletop lighting, still life beverage shot, clear separation between bottle and glass, distinct gap, static close-up, minimal camera movement`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_beer_glass_separation_phrase_ovaat.py`
   - `맥주` baseline과 separation phrase variant를 비교하는 OVAT 스크립트를 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-86-local-ltx-beer-glass-separation-phrase-ovaat/summary.json`

### aggregate

- baseline mid-frame MSE: `103.34`
- variant mid-frame MSE: `103.53`
- mid-frame MSE delta: `-0.19`
- edge variance delta: `-9.89`

### 확인된 것

1. separation phrase variant는 baseline과 사실상 차이가 없었습니다.
2. 수치상으로는 오히려 아주 소폭 나빠졌습니다.
3. 따라서 `clear separation between bottle and glass`는 현재 baseline 위에서 유효 레버가 아니었습니다.

## 6. 실패/제약

1. `맥주` 1장 기준입니다.
2. 이 결과는 phrase 자체가 무력하다는 뜻일 수 있고, 이미 `cover_bottom`으로 대부분 해결됐다는 뜻일 수도 있습니다.

## 7. 결론

- 가설 충족 여부: **실패**
- 판단:
  - `glass separation phrase`는 현재 baseline에 추가할 가치가 없습니다.
  - 다음 후속 레버는 separation prompt보다 다른 축이어야 합니다.

## 8. 다음 액션

1. 새 drink 샘플이 생기기 전까지는 현재 baseline을 유지하는 편이 맞습니다.
2. 다음은 drink lane보다 다른 샘플군으로 넘어가거나, video generation baseline 자체를 중간 점검하는 편이 낫습니다.

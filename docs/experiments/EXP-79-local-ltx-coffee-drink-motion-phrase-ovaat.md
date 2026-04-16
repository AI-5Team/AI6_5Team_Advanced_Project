# EXP-79 Local LTX coffee drink motion phrase OVAT

## 1. 기본 정보

- 실험 ID: `EXP-79`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / drink lane parity check`

## 2. 왜 이 작업을 했는가

- `EXP-78`에서 `맥주`는 `realistic drink commercial motion`보다 `still life beverage shot`가 훨씬 더 안정적이었습니다.
- 하지만 그 결과만으로는 `맥주 전용 예외`인지, `glass drink lane` 전체 기본값인지 구분할 수 없었습니다.
- 그래서 같은 `glass_drink_candidate -> cover_top` 샘플인 `커피` 1장에 같은 레버를 그대로 붙여 parity를 확인했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. 이미지: `커피`
4. prepare mode: `auto` (`resolved_prepare_mode = cover_top`)
5. negative prompt: 기본값
6. frames / steps / fps: `25 / 6 / 8`

### 이번에 바꾼 레버

- `drink motion phrase`만 바꿨습니다.
- baseline:
  - `iced coffee, bright tabletop lighting, realistic drink commercial motion, static close-up, minimal camera movement`
- variant:
  - `iced coffee, bright tabletop lighting, still life beverage shot, static close-up, minimal camera movement`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_coffee_drink_motion_phrase_ovaat.py`
   - `커피` 1장에서 baseline motion phrase와 still-life variant를 비교하는 OVAT 스크립트를 추가했습니다.
2. `scripts/local_video_ltx_batch_runner.py`
   - drink lane 기본 prompt를 `still life beverage shot`으로 올렸습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-79-local-ltx-coffee-drink-motion-phrase-ovaat/summary.json`

### aggregate

- baseline mid-frame MSE: `279.75`
- variant mid-frame MSE: `152.54`
- mid-frame MSE delta: `+127.21`
- edge variance delta: `+319.40`

### 확인된 것

1. `커피`도 `still life beverage shot` variant가 더 좋았습니다.
2. 시각적으로도 glass rim과 ice edge가 baseline보다 더 또렷했습니다.
3. 따라서 `still life beverage shot`는 `맥주 전용`이 아니라 현재 `glass drink lane` 공통 baseline 후보입니다.

## 6. 실패/제약

1. drink lane 근거는 아직 `커피`, `맥주` 2장뿐입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 현재 `glass_drink_candidate` baseline은 `cover_top + still life beverage shot`이 맞습니다.
  - `realistic drink commercial motion`을 기본값으로 둘 근거는 줄었습니다.

## 8. 다음 액션

1. `맥주`의 다음 병목인 bottle label / foam 보존 레버를 별도로 봅니다.
2. drink lane에 새 샘플이 생기면 현재 baseline이 유지되는지 다시 검증합니다.

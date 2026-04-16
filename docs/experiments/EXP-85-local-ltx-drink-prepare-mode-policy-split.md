# EXP-85 Local LTX drink prepare mode policy split

## 1. 기본 정보

- 실험 ID: `EXP-85`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / drink lane baseline policy`

## 2. 왜 이 작업을 했는가

- `EXP-79`, `EXP-83`, `EXP-84`를 거치면서 drink lane baseline은 개별 샘플 수준에서는 정리됐습니다.
- 하지만 아직 `정말로 정책으로 승격해도 되는가`는 `커피 + 맥주`를 묶은 비교가 없었습니다.
- 그래서 이번에는 옛 policy(`둘 다 cover_top`)와 현재 policy(`커피 cover_top, 맥주 cover_bottom`)만 비교하는 묶음 실험을 진행했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. 이미지 세트:
   - `커피`
   - `맥주`
4. prompt family:
   - 둘 다 `still life beverage shot`
5. negative prompt: 기본값
6. frames / steps / fps: `25 / 6 / 8`

### 이번에 바꾼 레버

- `drink prepare-mode policy`만 바꿨습니다.
- baseline policy:
  - `커피 = cover_top`
  - `맥주 = cover_top`
- variant policy:
  - `커피 = cover_top`
  - `맥주 = cover_bottom`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_drink_prepare_mode_policy_split.py`
   - `커피/맥주`를 묶어서 old/new drink policy를 비교하는 스크립트를 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-85-local-ltx-drink-prepare-mode-policy-split/summary.json`

### aggregate

- baseline avg mid-frame MSE: `210.67`
- variant avg mid-frame MSE: `127.94`
- avg mid-frame MSE delta: `+82.73`
- avg edge variance delta: `+143.40`

### per image

1. `커피`
   - 변화 없음
   - `cover_top -> cover_top`
2. `맥주`
   - mid-frame MSE delta: `+165.45`
   - edge variance delta: `+286.81`
   - `cover_top -> cover_bottom`

### 확인된 것

1. 현재 drink policy는 aggregate 기준으로도 old policy보다 명확히 더 좋았습니다.
2. `커피`는 유지되고, 개선은 전부 `맥주` 쪽에서 나왔습니다.
3. 따라서 `top-heavy drink = cover_top`, `bottom-heavy bottle+glass = cover_bottom` 분기는 baseline 승격이 맞습니다.

## 6. 실패/제약

1. drink lane 근거는 아직 `커피`, `맥주` 2장뿐입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 현재 drink lane prepare-mode policy는 단일 규칙보다 구조 기반 분기가 맞습니다.
  - baseline 승격 판단은 타당합니다.

## 8. 다음 액션

1. 다음은 `맥주` baseline 위에서 bottle/glass separation phrase가 실제로 추가 이득이 있는지 봅니다.
2. 새 drink 샘플이 생기면 지금 분기가 유지되는지 재검증해야 합니다.

# EXP-77 Local LTX tray steam default policy split

## 1. 기본 정보

- 실험 ID: `EXP-77`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / tray-full-plate baseline policy`

## 2. 왜 이 작업을 했는가

- `EXP-74`에서는 `타코야키`가 no-steam 쪽에서 크게 좋아졌고, `EXP-76`에서는 `규카츠`도 소폭 no-steam 쪽이 나았습니다.
- 이제 필요한 판단은 `타코야키 전용 예외`가 아니라, `tray/full-plate 기본 prompt 정책을 steam on에서 steam off로 바꿔도 되는가`였습니다.
- 그래서 이번에는 `규카츠`, `타코야키` 두 장을 같은 조건으로 묶고, 바꾸는 변수는 `steam default on/off` 하나만 두었습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. 이미지 세트:
   - `규카츠`
   - `타코야키`
4. prepare mode: `auto` (`resolved_prepare_mode = cover_center`)
5. negative prompt: 기본값
6. frames / steps / fps: `25 / 6 / 8`

### 이번에 바꾼 레버

- `tray/full-plate steam default`만 바꿨습니다.
- baseline policy:
  - `strong steam cloud` 포함
- variant policy:
  - `strong steam cloud` 제거

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_tray_steam_default_policy_split.py`
   - `규카츠`, `타코야키` 2장에 대해 tray baseline policy를 `steam on/off`로 비교하는 스크립트를 추가했습니다.
2. `scripts/local_video_ltx_batch_runner.py`
   - reusable runner의 tray/full-plate 기본 prompt를 `steam off`로 맞췄습니다.
   - 현재 runner baseline은 `규카츠`, `타코야키`에 대해 `strong steam cloud`를 기본값에서 제거합니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-77-local-ltx-tray-steam-default-policy-split/summary.json`

### aggregate

- baseline avg mid-frame MSE: `753.46`
- variant avg mid-frame MSE: `312.40`
- avg mid-frame MSE delta: `+441.06`
- baseline avg edge variance: `1663.05`
- variant avg edge variance: `1861.88`
- avg edge variance delta: `+198.83`

### per image

1. `규카츠`
   - mid-frame MSE delta: `+8.75`
   - edge variance delta: `+22.34`
2. `타코야키`
   - mid-frame MSE delta: `+873.36`
   - edge variance delta: `+375.32`

### 확인된 것

1. `tray/full-plate` 2장 모두에서 `steam off`가 `steam on`보다 나았습니다.
2. `규카츠`에서는 개선 폭이 작지만 방향은 동일했고, `타코야키`에서는 개선 폭이 매우 컸습니다.
3. 현재 데이터 기준으로는 `tray subtype split`보다 `tray/full-plate 기본값 = no steam`이 더 적절합니다.

## 6. 실패/제약

1. tray/full-plate 근거는 아직 `규카츠`, `타코야키` 2장뿐입니다.
2. `steam off`가 `tray/full-plate` 전체에 일반화되는지는 더 많은 실사 샘플이 필요합니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 현재 single-photo tray/full-plate baseline은 `cover_center + no steam`이 맞습니다.
  - 적어도 현재 샘플 조건에서는 `steam on`을 기본값으로 둘 근거가 없습니다.

## 8. 다음 액션

1. 다음은 `맥주`처럼 분기는 맞지만 결과가 거친 샘플에 대해 drink 전용 후속 레버를 보는 것이 맞습니다.
2. tray/full-plate 쪽은 새로운 실사 샘플이 생기기 전까지 `cover_center + no steam`을 현재 baseline으로 유지합니다.

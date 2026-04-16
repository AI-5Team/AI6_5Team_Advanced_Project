# EXP-76 Local LTX gyukatsu steam phrase OVAT

## 1. 기본 정보

- 실험 ID: `EXP-76`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / tray-full-plate 후속 레버`

## 2. 왜 이 작업을 했는가

- `EXP-74`에서 `타코야키`는 `strong steam cloud`를 제거했을 때 크게 좋아졌습니다.
- 하지만 그 결과만으로는 `타코야키 전용 예외`인지, `tray/full-plate` 전체 정책인지 구분하기 어려웠습니다.
- 그래서 같은 `tray_full_plate -> cover_center` 샘플인 `규카츠` 1장에 대해 같은 레버만 다시 붙였습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. 이미지: `규카츠`
4. prepare mode: `auto` (`resolved_prepare_mode = cover_center`)
5. negative prompt: 기본값
6. frames / steps / fps: `25 / 6 / 8`

### 이번에 바꾼 레버

- `steam phrase`만 바꿨습니다.
- baseline:
  - `crispy gyukatsu, bright tabletop lighting, strong steam cloud, realistic food motion, static close-up, minimal camera movement`
- variant:
  - `crispy gyukatsu, bright tabletop lighting, realistic food motion, static close-up, minimal camera movement`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_gyukatsu_steam_phrase_ovaat.py`
   - `규카츠` 1장에서 `steam on/off`만 비교하는 OVAT 스크립트를 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-76-local-ltx-gyukatsu-steam-phrase-ovaat/summary.json`

### aggregate

- mid-frame MSE delta: `+8.75`
- edge variance delta: `+22.34`

### 확인된 것

1. `strong steam cloud`를 제거한 variant가 수치상 조금 더 좋았습니다.
2. `규카츠`에서는 `타코야키`처럼 큰 차이는 아니었지만, no-steam 쪽이 baseline보다 나빠지진 않았습니다.
3. 따라서 현재 데이터는 `규카츠 steam on / 타코야키 steam off` 같은 강한 subtype 분기보다, `tray/full-plate 기본값을 steam off로 둘 가능성`을 더 지지합니다.

## 6. 실패/제약

1. `규카츠` 개선 폭은 작아서, 이 결과만으로 강한 subtype split을 결론내리긴 어렵습니다.
2. 여전히 `tray/full-plate` 샘플은 `규카츠`, `타코야키` 2장뿐입니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `규카츠`에서는 `steam phrase 제거`가 대승 레버는 아니었습니다.
  - 하지만 적어도 `tray/full-plate` 기본값을 `steam off`로 둘 후보로는 충분합니다.

## 8. 다음 액션

1. 다음은 `규카츠 + 타코야키`를 묶어서 `tray/full-plate steam default on/off`를 직접 비교하는 것입니다.
2. 그 결과가 일관되면 reusable batch runner의 tray prompt 기본값도 그쪽으로 정리할 수 있습니다.

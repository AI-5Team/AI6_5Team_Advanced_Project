# EXP-66 Local LTX prepare_mode policy split

## 1. 기본 정보

- 실험 ID: `EXP-66`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / single-photo prepare_mode baseline 정책화`

## 2. 왜 이 작업을 했는가

- `EXP-65`에서 `contain_blur`가 `6개 중 5개`에서 더 좋았지만, `규카츠`처럼 이미 프레임을 꽉 채운 트레이샷은 `cover_center`가 더 좋았습니다.
- 따라서 다음 단계는 global prepare_mode를 하나로 고정하는 것이 아니라, 현재 샘플 조건에 맞는 최소 분기 정책이 실제로 더 나은지 확인하는 것이었습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. prompt: 음식 라벨 + `bright tabletop lighting + strong steam cloud + static close-up`
4. negative prompt: 기본값
5. frames / steps / fps: `25 / 6 / 8`
6. 이미지:
   - `규카츠`
   - `라멘`
   - `순두부짬뽕`
   - `장어덮밥`
   - `커피`
   - `아이스크림`

### 이번에 바꾼 레버

- `prepare_mode policy`만 바꿨습니다.
- baseline: 전체 이미지 `contain_blur`
- variant policy:
  - `규카츠`: `cover_center`
  - 나머지: `contain_blur`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_prepare_mode_policy_split.py`
   - global `contain_blur` baseline과 `규카츠만 cover_center`인 policy variant를 비교하도록 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-66-local-ltx-prepare-mode-policy-split/summary.json`

### 이미지별 결과

1. 규카츠
   - policy가 더 좋았습니다.
   - mid-frame MSE delta: `+321.86`
2. 라멘
   - 변화 없음
3. 순두부짬뽕
   - 변화 없음
4. 장어덮밥
   - 변화 없음
5. 커피
   - 변화 없음
6. 아이스크림
   - 변화 없음

### aggregate

- policy가 더 나은 이미지는 `6개 중 1개`였습니다.
- average mid-frame MSE delta는 `+53.64`였습니다.
- average edge variance delta는 `+85.76`이었습니다.

### 확인된 것

1. `규카츠`처럼 이미 꽉 찬 트레이샷은 global `contain_blur`보다 `cover_center` 예외를 두는 편이 맞습니다.
2. 나머지 5장에는 회귀가 없었습니다.
3. 즉 `샷 타입 -> prepare_mode` 분기는 현재 single-photo 조건에서 실제 baseline 후보가 됩니다.

## 6. 실패/제약

1. 이 policy는 사실상 `규카츠` 1건만 바꾸는 작은 분기입니다.
2. 아직 `drink`, `dessert` 쪽 예외는 검증되지 않았습니다.
3. seed `7` 고정 기준입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - global `contain_blur`보다는 `tray/full-plate 예외`가 있는 정책 baseline이 더 맞습니다.
  - 다음 실험은 이 정책 위에서 `preserve-shot 내부 예외`를 더 볼 수 있습니다.

## 8. 다음 액션

1. 다음 레버는 `preserve-shot 내부 top bias`입니다.
2. 예:
   - bowl / soup / drink / dessert 기본값은 `contain_blur`
   - 그 안에서 `cover_top`이 더 나은 하위 타입이 있는지 확인

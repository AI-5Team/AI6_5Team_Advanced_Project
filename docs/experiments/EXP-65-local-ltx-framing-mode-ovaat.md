# EXP-65 Local LTX framing mode OVAT

## 1. 기본 정보

- 실험 ID: `EXP-65`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / single-photo 입력 프레이밍`

## 2. 왜 이 작업을 했는가

- 현재 샘플은 사용자가 식사 중에 직접 찍어 둔 사진입니다.
- 즉 다른 각도나 다른 샷을 새로 요구하는 실험은 의미가 약합니다.
- 그래서 이번에는 prompt가 아니라, 같은 사진 한 장을 모델에 넣기 전에 어떻게 프레이밍하느냐가 더 큰 레버인지 확인했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. prompt: 음식 라벨 + generic baseline prompt
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

- `prepare_mode`만 바꿨습니다.
- baseline: `cover_center`
- variant: `contain_blur`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_first_try.py`
   - `--prepare-mode`를 추가했습니다.
   - 지원 모드:
     - `cover_center`
     - `cover_top`
     - `contain_blur`
2. `scripts/local_video_ltx_framing_mode_ovaat.py`
   - 같은 이미지 세트에 대해 `cover_center`와 `contain_blur`만 비교하도록 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-65-local-ltx-framing-mode-ovaat/summary.json`

### 이미지별 결과

1. 규카츠
   - `cover_center`가 더 좋았습니다.
   - mid-frame MSE delta: `-321.86`
2. 라멘
   - `contain_blur`가 크게 더 좋았습니다.
   - mid-frame MSE delta: `+621.96`
3. 순두부짬뽕
   - `contain_blur`가 더 좋았습니다.
   - mid-frame MSE delta: `+216.17`
4. 장어덮밥
   - `contain_blur`가 크게 더 좋았습니다.
   - mid-frame MSE delta: `+711.55`
5. 커피
   - `contain_blur`가 더 좋았습니다.
   - mid-frame MSE delta: `+34.52`
6. 아이스크림
   - `contain_blur`가 약간 더 좋았습니다.
   - mid-frame MSE delta: `+4.50`

### aggregate

- `contain_blur`가 더 나은 이미지는 `6개 중 5개`였습니다.
- average mid-frame MSE delta는 `+211.14`였습니다.
- average edge variance delta는 `-176.20`이었습니다.

### 확인된 것

1. 현재 샘플 제약에서는 prompt보다 `입력 프레이밍 방식`이 더 큰 레버입니다.
2. 특히 bowl/tray/drink/dessert처럼 원본 구도를 최대한 보존해야 하는 사진에서는 `contain_blur`가 유리했습니다.
3. 반대로 규카츠처럼 이미 가득 찬 트레이샷은 `cover_center`가 더 좋았습니다.

## 6. 실패/제약

1. `contain_blur`는 배경 패드가 들어가므로 edge variance는 대체로 낮아졌습니다.
2. 규카츠처럼 이미 화면을 잘 채우는 샷에서는 오히려 손해였습니다.
3. 이번 실험은 seed `7` 고정 기준입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 현재 제약 조건에서는 `구도 재분기`보다 먼저 `프레이밍 보존 전략`을 baseline에 반영하는 편이 맞습니다.
  - 다음 baseline은 단일 `cover_center`가 아니라 샷 타입별 `prepare_mode` 분기여야 합니다.

## 8. 다음 액션

1. 다음 레버는 `사진 자체 구도 분류`입니다.
2. 예:
   - bowl / soup / dessert / drink: `contain_blur`
   - tray set / full plate: `cover_center`

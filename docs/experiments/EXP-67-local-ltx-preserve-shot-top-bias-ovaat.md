# EXP-67 Local LTX preserve-shot top bias OVAT

## 1. 기본 정보

- 실험 ID: `EXP-67`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / preserve-shot refine`

## 2. 왜 이 작업을 했는가

- `EXP-66`으로 `규카츠는 cover_center`, 나머지는 `contain_blur`가 맞는다는 baseline 후보가 생겼습니다.
- 여기서 다음 질문은 `contain_blur`가 이긴 preserve-shot 그룹 안에서도 `cover_top` 같은 top-bias crop이 더 나은 하위 타입이 있는지였습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. prompt: 음식 라벨 + current LTX baseline prompt
4. negative prompt: 기본값
5. frames / steps / fps: `25 / 6 / 8`
6. 이미지:
   - `라멘`
   - `순두부짬뽕`
   - `장어덮밥`
   - `커피`
   - `아이스크림`

### 이번에 바꾼 레버

- `prepare_mode`만 바꿨습니다.
- baseline: `contain_blur`
- variant: `cover_top`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_preserve_shot_top_bias_ovaat.py`
   - preserve-shot subset에 대해 `contain_blur`와 `cover_top`만 비교하도록 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-67-local-ltx-preserve-shot-top-bias-ovaat/summary.json`

### 이미지별 결과

1. 라멘
   - `cover_top`이 크게 나빴습니다.
   - mid-frame MSE delta: `-491.58`
2. 순두부짬뽕
   - `cover_top`이 나빴습니다.
   - mid-frame MSE delta: `-91.01`
3. 장어덮밥
   - `cover_top`이 크게 나빴습니다.
   - mid-frame MSE delta: `-1146.54`
4. 커피
   - `cover_top`이 더 좋았습니다.
   - mid-frame MSE delta: `+32.27`
5. 아이스크림
   - `cover_top`이 약간 나빴습니다.
   - mid-frame MSE delta: `-4.50`

### aggregate

- `cover_top`이 더 나은 이미지는 `5개 중 1개`였습니다.
- average mid-frame MSE delta는 `-340.27`이었습니다.
- average edge variance delta는 `+128.90`이었습니다.

### 확인된 것

1. `cover_top`은 preserve-shot 그룹의 일반 해법이 아닙니다.
2. 특히 bowl/soup 계열에서는 `contain_blur`를 유지하는 편이 확실히 낫습니다.
3. 다만 `커피` 1건에서는 `cover_top`이 더 좋아, drink 전용 예외 가능성은 남았습니다.

## 6. 실패/제약

1. 이번 결과는 `커피` 1장만 drink 샘플로 포함합니다.
2. `edge variance`는 `cover_top`이 커 보일 수 있지만, aggregate 품질 개선과는 일치하지 않았습니다.
3. seed `7` 고정 기준입니다.

## 7. 결론

- 가설 충족 여부: **미충족**
- 판단:
  - `cover_top`은 preserve-shot의 기본값이 될 수 없습니다.
  - 다만 `커피`처럼 세로 드링크 컷에서는 좁은 예외 정책을 다시 볼 가치는 있습니다.

## 8. 다음 액션

1. 다음 레버는 `drink 전용 예외 정책`입니다.
2. baseline policy(`규카츠=cover_center`, 그 외=`contain_blur`) 위에 `커피만 cover_top`을 얹었을 때 regression 없이 이득이 생기는지 확인합니다.

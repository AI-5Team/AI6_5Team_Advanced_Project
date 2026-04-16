# EXP-58 Local LTX baseline multi-image validation

## 1. 기본 정보

- 실험 ID: `EXP-58`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 이미지-투-비디오 baseline 다건 검증`

## 2. 왜 이 작업을 했는가

- `EXP-56`까지의 결과를 보면 prompt phrasing 자체로 큰 개선을 만들 수 있는 레버가 거의 남지 않았습니다.
- 그래서 다음 단계로, 현재 가장 낫다고 본 `LTX baseline`이 다른 실제 음식 사진에도 유지되는지 먼저 확인해야 했습니다.

## 3. baseline

### 고정한 조건

1. 하드웨어: `RTX 4080 SUPER 16GB / RAM 64GB`
2. 모델: `Lightricks/LTX-Video` + `city96/LTX-Video-gguf / ltx-video-2b-v0.9-Q3_K_S.gguf`
3. 설정: `25프레임 / 6스텝 / 8fps / guidance 3.0 / seed 7`
4. prompt 형태: `bright tabletop lighting + strong steam cloud + realistic food motion + static close-up`
5. negative prompt: 기본값 유지

### 검증 이미지

1. `음식사진샘플(규카츠).jpg`
2. `음식사진샘플(라멘).jpg`
3. `음식사진샘플(순두부짬뽕).jpg`
4. `음식사진샘플(장어덮밥).jpg`

## 4. 무엇을 바꿨는가

- 재현용 스크립트 `scripts/local_video_ltx_baseline_multi_image_validation.py`를 추가했습니다.
- 파일명에 따라 음식 라벨만 바꾸고, 나머지 baseline prompt 구조는 동일하게 유지했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-58-local-ltx-baseline-multi-image-validation/summary.json`
- 대표 프레임:
  - `규카츠/ltx_first_try_mid_frame.png`
  - `라멘/ltx_first_try_mid_frame.png`
  - `순두부짬뽕/ltx_first_try_mid_frame.png`
  - `장어덮밥/ltx_first_try_mid_frame.png`

### baseline 다건 결과

- 규카츠
  - mid frame MSE: `246.90`
  - edge variance: `1952.13`
  - 판단: 가장 안정적
- 라멘
  - mid frame MSE: `720.39`
  - edge variance: `447.18`
  - 판단: 국물/면 구조가 크게 흐려짐
- 순두부짬뽕
  - mid frame MSE: `596.56`
  - edge variance: `642.31`
  - 판단: 편차 큼
- 장어덮밥
  - mid frame MSE: `924.08`
  - edge variance: `1493.71`
  - 판단: 정지 프레임은 보이지만 왜곡이 큼

### 확인된 것

1. 현재 `LTX baseline`은 규카츠 같은 샘플에는 맞지만 음식군 전반으로 일반화되지는 않습니다.
2. 특히 라멘과 장어덮밥처럼 형태/질감이 다른 음식에서 품질 편차가 큽니다.
3. 따라서 다음 연구선은 prompt phrasing보다 `입력 이미지군별 안정성`을 먼저 보는 편이 맞습니다.

## 6. 실패/제약

1. 이번 다건 검증은 4장 기준입니다.
2. 음식 라벨은 파일명 기반 단순 매핑이라 더 정교한 product prompt는 아닙니다.
3. 단일 seed 기준이라 seed 편차까지는 아직 확인하지 않았습니다.

## 7. 결론

- 가설 충족 여부: **미충족**
- 판단:
  - 현재 LTX baseline은 특정 음식군에서는 쓸 만하지만, 전반적 baseline으로 승격하기엔 아직 이릅니다.
  - 다음은 `sample image 다양화` 또는 `seed 안정성`이 우선입니다.

## 8. 다음 액션

1. 같은 음식에 대해 seed를 바꿔 안정성 편차를 봅니다.
2. 음식군별로 prompt template을 분리해야 하는지 판단합니다.

# EXP-54 Local LTX-Video food motion phrase OVAT

## 1. 기본 정보

- 실험 ID: `EXP-54`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 이미지-투-비디오 프롬프트 OVAT`

## 2. 왜 이 작업을 했는가

- `EXP-52`까지의 결과를 보면 `texture emphasis`는 유효 레버가 아니었습니다.
- 따라서 다음 후보로, 음식 장면의 움직임을 더 직접적으로 규정하는 `food motion phrase`를 한 변수로 확인할 필요가 있었습니다.

## 3. baseline

### 고정한 조건

1. 하드웨어: `RTX 4080 SUPER 16GB / RAM 64GB`
2. 모델: `Lightricks/LTX-Video` + `city96/LTX-Video-gguf / ltx-video-2b-v0.9-Q3_K_S.gguf`
3. 입력 이미지: `docs/sample/음식사진샘플(규카츠).jpg`
4. 설정: `25프레임 / 6스텝 / 8fps / guidance 3.0 / seed 7`
5. 공통 prompt: `bright tabletop lighting, strong steam cloud, static close-up, minimal camera movement`
6. 바뀐 변수: `food motion phrase`만 변경

### 비교 대상

- baseline: `realistic food motion`
- variant: `subtle sizzling food motion`

## 4. 무엇을 바꿨는가

- 재현용 스크립트 `scripts/local_video_ltx_food_motion_ovaat.py`를 추가했습니다.
- 동일 조건에서 motion phrase만 바꾸고 `first/mid frame` heuristic을 비교했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-54-local-ltx-video-food-motion-phrase-ovaat/summary.json`
- `docs/experiments/artifacts/exp-54-local-ltx-video-food-motion-phrase-ovaat/baseline-realistic-motion/ltx_first_try_mid_frame.png`
- `docs/experiments/artifacts/exp-54-local-ltx-video-food-motion-phrase-ovaat/variant-sizzling-motion/ltx_first_try_mid_frame.png`

### baseline 대비 차이

- 실행 시간
  - baseline: `11.75초`
  - variant: `11.20초`
- mid frame heuristic
  - baseline MSE: `246.90`
  - variant MSE: `257.19`
  - baseline edge variance: `1952.13`
  - variant edge variance: `1942.39`
- 관찰
  - `subtle sizzling food motion`은 약간 더 빠르긴 했지만 음식 구조 보존은 baseline보다 나아지지 않았습니다.
  - 규카츠 결과 접시 윤곽은 `realistic food motion`이 더 안정적이었습니다.

### 확인된 것

1. 이번 샘플에서는 `food motion phrase`도 baseline을 이기지 못했습니다.
2. `subtle sizzling` 같은 더 구체적인 motion phrase가 항상 품질을 올리지는 않았습니다.
3. 현재 baseline은 여전히 `realistic food motion` 쪽이 낫습니다.

## 6. 실패/제약

1. 이번 판단은 단일 이미지 1장 기준입니다.
2. 다른 음식군에서는 `sizzling` 표현이 더 잘 맞을 수 있습니다.
3. frame heuristic만으로는 실제 clip의 리듬감까지 모두 설명하지 못합니다.

## 7. 결론

- 가설 충족 여부: **미충족**
- 판단:
  - `food motion phrase`는 현재 샘플에선 baseline 승격 레버가 아닙니다.
  - 다음 LTX 레버는 `negative phrase`나 `sample image 다양화`가 더 적절합니다.

## 8. 다음 액션

1. 다음 OVAT는 `negative phrase`를 보는 편이 맞습니다.
2. 이후에는 메뉴 사진을 바꿔 재현성을 다시 확인합니다.

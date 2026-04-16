# EXP-56 Local LTX-Video negative prompt OVAT

## 1. 기본 정보

- 실험 ID: `EXP-56`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 이미지-투-비디오 프롬프트 OVAT`

## 2. 왜 이 작업을 했는가

- `EXP-54`까지의 결과를 보면 positive prompt 쪽 세부 phrasing은 baseline을 잘 넘지 못했습니다.
- 그래서 다음 후보로, artifact 억제를 위해 stronger negative prompt를 넣는 방식이 실제로 도움이 되는지 확인해야 했습니다.

## 3. baseline

### 고정한 조건

1. 하드웨어: `RTX 4080 SUPER 16GB / RAM 64GB`
2. 모델: `Lightricks/LTX-Video` + `city96/LTX-Video-gguf / ltx-video-2b-v0.9-Q3_K_S.gguf`
3. 입력 이미지: `docs/sample/음식사진샘플(규카츠).jpg`
4. 설정: `25프레임 / 6스텝 / 8fps / guidance 3.0 / seed 7`
5. 공통 prompt: `crispy gyukatsu, bright tabletop lighting, strong steam cloud, realistic food motion, static close-up, minimal camera movement`
6. 바뀐 변수: `negative prompt`만 변경

### 비교 대상

- baseline: `worst quality, blurry, jittery, distorted, warped, overexposed, text, watermark`
- variant: `baseline + ghosting / duplicated utensils / malformed cutlet / extra food pieces`

## 4. 무엇을 바꿨는가

- `local_video_ltx_first_try.py`에 `--negative-prompt` override를 추가했습니다.
- 재현용 스크립트 `scripts/local_video_ltx_negative_prompt_ovaat.py`를 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-56-local-ltx-video-negative-prompt-ovaat/summary.json`
- `docs/experiments/artifacts/exp-56-local-ltx-video-negative-prompt-ovaat/baseline-default-negative/ltx_first_try_mid_frame.png`
- `docs/experiments/artifacts/exp-56-local-ltx-video-negative-prompt-ovaat/variant-stronger-negative/ltx_first_try_mid_frame.png`

### baseline 대비 차이

- 실행 시간
  - baseline: `12.35초`
  - variant: `11.71초`
- mid frame heuristic
  - baseline MSE: `246.90`
  - variant MSE: `384.47`
  - baseline edge variance: `1952.13`
  - variant edge variance: `1795.04`
- 관찰
  - stronger negative prompt는 속도는 약간 빨랐지만 음식 구조를 크게 망쳤습니다.
  - 규카츠 중앙부와 샐러드, 국물 영역이 더 흐려졌고, 전체적으로 디테일이 죽었습니다.

### 확인된 것

1. 이번 샘플에서는 stronger negative prompt가 명확히 해로웠습니다.
2. 단순히 negative phrase를 더 많이 넣는다고 artifact 억제가 좋아지지 않았습니다.
3. 현재 baseline은 기본 negative prompt를 유지하는 편이 맞습니다.

## 6. 실패/제약

1. 이번 판단은 단일 이미지 1장 기준입니다.
2. 다른 음식군에서는 결과가 다를 수 있습니다.
3. stronger negative prompt는 phrasing 하나가 아니라 묶음 제약이라 세부 원인 분리는 아직 안 됐습니다.

## 7. 결론

- 가설 충족 여부: **미충족**
- 판단:
  - stronger negative prompt는 현재 baseline 승격 레버가 아닙니다.
  - 이제 prompt 레버보다 `입력 이미지 다양화` 또는 `steps/frame` 재조합이 더 의미 있을 수 있습니다.

## 8. 다음 액션

1. 같은 baseline으로 음식 사진을 바꿔 재현성을 확인합니다.
2. 이후에는 `sample image 다양화`나 `seed 안정성` 쪽을 보는 편이 맞습니다.

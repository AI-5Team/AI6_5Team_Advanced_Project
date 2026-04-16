# EXP-52 Local LTX-Video texture emphasis OVAT

## 1. 기본 정보

- 실험 ID: `EXP-52`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 이미지-투-비디오 프롬프트 OVAT`

## 2. 왜 이 작업을 했는가

- `EXP-51`에서 `bright tabletop lighting`가 현재 가장 나은 food-shot baseline으로 올라왔습니다.
- 다음 후보 레버는 음식 디테일을 더 살릴 수 있을지 확인하는 `texture emphasis`였습니다.

## 3. baseline

### 고정한 조건

1. 하드웨어: `RTX 4080 SUPER 16GB / RAM 64GB`
2. 모델: `Lightricks/LTX-Video` + `city96/LTX-Video-gguf / ltx-video-2b-v0.9-Q3_K_S.gguf`
3. 입력 이미지: `docs/sample/음식사진샘플(규카츠).jpg`
4. 설정: `25프레임 / 6스텝 / 8fps / guidance 3.0 / seed 7`
5. 공통 prompt suffix: `bright tabletop lighting, strong steam cloud, realistic food motion, static close-up, minimal camera movement`
6. 바뀐 변수: `texture emphasis`만 변경

### 비교 대상

- baseline: `no explicit texture phrase`
- variant: `detailed crispy breading texture`

## 4. 무엇을 바꿨는가

- 재현용 스크립트 `scripts/local_video_ltx_texture_ovaat.py`를 추가했습니다.
- 동일 설정에서 texture phrase만 다르게 넣고 `first/mid frame` heuristic을 비교했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-52-local-ltx-video-texture-emphasis-ovaat/summary.json`
- `docs/experiments/artifacts/exp-52-local-ltx-video-texture-emphasis-ovaat/baseline-no-texture/ltx_first_try_mid_frame.png`
- `docs/experiments/artifacts/exp-52-local-ltx-video-texture-emphasis-ovaat/variant-crispy-texture/ltx_first_try_mid_frame.png`

### baseline 대비 차이

- 실행 시간
  - baseline: `11.55초`
  - variant: `11.58초`
- mid frame heuristic
  - baseline MSE: `246.90`
  - variant MSE: `250.69`
  - baseline edge variance: `1952.13`
  - variant edge variance: `1877.06`
- 관찰
  - `detailed crispy breading texture`를 추가해도 규카츠 결이 더 또렷해지지 않았습니다.
  - 오히려 mid frame 기준으로는 접시/고기 경계가 약간 더 무뎌졌습니다.

### 확인된 것

1. 이번 샘플에서는 `texture emphasis`가 유효 레버가 아니었습니다.
2. 현재 `LTX` baseline은 굳이 texture phrase를 더 얹지 않는 편이 낫습니다.
3. `bright tabletop lighting + strong steam cloud + static close-up` 조합이 계속 baseline 유지 후보입니다.

## 6. 실패/제약

1. 이번 판단은 단일 이미지 1장 기준입니다.
2. 다른 음식에서는 texture phrase가 달라질 수 있습니다.
3. frame heuristic만으로는 바삭함의 체감까지 완전히 설명하긴 어렵습니다.

## 7. 결론

- 가설 충족 여부: **미충족**
- 판단:
  - `texture emphasis`는 현재 샘플에선 baseline을 이기지 못했습니다.
  - 다음 LTX 레버는 `food motion phrase`나 `negative phrase` 쪽이 더 유망합니다.

## 8. 다음 액션

1. 다음 OVAT는 `food motion phrase` 또는 `negative phrase`로 이어갑니다.
2. texture 관련 레버는 다른 음식군에서 다시 검증하기 전까지 우선순위를 낮춥니다.

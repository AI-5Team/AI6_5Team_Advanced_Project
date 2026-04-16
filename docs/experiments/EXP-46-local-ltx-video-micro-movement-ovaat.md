# EXP-46 Local LTX-Video micro movement OVAT

## 1. 기본 정보

- 실험 ID: `EXP-46`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 이미지-투-비디오 프롬프트 OVAT`

## 2. 왜 이 작업을 했는가

- `EXP-44`에서 현재 `LTX` food shot baseline은 `static close-up, minimal camera movement` 쪽이 더 안정적이라는 점을 확인했습니다.
- 그래서 이번에는 같은 정적 baseline을 유지한 채, `micro movement`만 아주 약하게 넣었을 때 clip 품질이 더 좋아지는지 확인했습니다.

## 3. baseline

### 고정한 조건

1. 하드웨어: `RTX 4080 SUPER 16GB / RAM 64GB`
2. 모델: `Lightricks/LTX-Video` + `city96/LTX-Video-gguf / ltx-video-2b-v0.9-Q3_K_S.gguf`
3. 입력 이미지: `docs/sample/음식사진샘플(규카츠).jpg`
4. 설정: `25프레임 / 6스텝 / 8fps / guidance 3.0 / seed 7`
5. 공통 prompt prefix: `crispy gyukatsu, gentle steam, warm restaurant lighting, realistic food motion`
6. 바뀐 변수: `camera motion phrase`만 변경

### 비교 대상

- baseline: `static close-up, minimal camera movement`
- variant: `static close-up, subtle camera drift`

## 4. 무엇을 바꿨는가

- 기존 `scripts/local_video_ltx_camera_motion_ovaat.py`를 재사용했습니다.
- 실행 시 baseline/variant motion만 CLI로 바꿨습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-46-local-ltx-video-micro-movement-ovaat/summary.json`
- `docs/experiments/artifacts/exp-46-local-ltx-video-micro-movement-ovaat/baseline-push-in/ltx_first_try_mid_frame.png`
- `docs/experiments/artifacts/exp-46-local-ltx-video-micro-movement-ovaat/variant-static-close-up/ltx_first_try_mid_frame.png`

### baseline 대비 차이

- 실행 시간
  - baseline: `11.43초`
  - variant: `11.56초`
- mid frame heuristic
  - baseline MSE: `361.05`
  - variant MSE: `481.27`
- 관찰
  - `subtle camera drift`를 넣자 규카츠 표면과 소스 칸 경계가 다시 퍼졌습니다.
  - 이번 샘플에서는 `micro movement`가 개선이 아니라 품질 저하로 보였습니다.

### 확인된 것

1. 현재 `LTX` baseline에서는 `micro movement`를 추가하지 않는 편이 더 낫습니다.
2. 음식 구조 보존을 우선할 때는 `minimal camera movement`를 유지하는 쪽이 맞습니다.
3. 즉 이번 레버는 실패 레버로 분류하는 편이 적절합니다.

## 6. 실패/제약

1. 이번 판단은 단일 이미지 1장 기준입니다.
2. clip 전체 움직임 체감은 추가로 볼 수 있지만, mid frame 기준으로는 이미 불리한 신호가 분명했습니다.

## 7. 결론

- 가설 충족 여부: **미충족**
- 판단:
  - `static close-up` baseline은 유지합니다.
  - 다음 LTX 레버는 motion이 아니라 `steam intensity` 또는 음식/조명 phrasing 쪽이 더 적절합니다.

## 8. 다음 액션

1. 다음 OVAT는 `steam intensity` 또는 `lighting phrase`로 이어갑니다.
2. `micro movement`는 현재 후보군에서 우선순위를 내립니다.

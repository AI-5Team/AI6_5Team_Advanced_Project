# EXP-44 Local LTX-Video camera motion phrase OVAT

## 1. 기본 정보

- 실험 ID: `EXP-44`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 이미지-투-비디오 프롬프트 OVAT`

## 2. 왜 이 작업을 했는가

- `EXP-40`과 `EXP-42`를 거치며 현재 `LTX` baseline은 `short prompt + 25프레임` 쪽이 더 적절해졌습니다.
- 다음으로는 같은 prompt 길이와 같은 프레임 수를 유지한 채, `camera motion phrase`만 바꿨을 때 음식 구조 보존이 달라지는지 확인해야 했습니다.

## 3. baseline

### 고정한 조건

1. 하드웨어: `RTX 4080 SUPER 16GB / RAM 64GB`
2. 모델: `Lightricks/LTX-Video` + `city96/LTX-Video-gguf / ltx-video-2b-v0.9-Q3_K_S.gguf`
3. 입력 이미지: `docs/sample/음식사진샘플(규카츠).jpg`
4. 설정: `25프레임 / 6스텝 / 8fps / guidance 3.0 / seed 7`
5. 공통 prompt prefix: `crispy gyukatsu, gentle steam, warm restaurant lighting, realistic food motion`
6. 바뀐 변수: `camera motion phrase`만 변경

### 비교 대상

- baseline: `slow push-in`
- variant: `static close-up, minimal camera movement`

## 4. 무엇을 바꿨는가

- 재현용 스크립트 `scripts/local_video_ltx_camera_motion_ovaat.py`를 추가했습니다.
- wrapper 스크립트는 `local_video_ltx_first_try.py`를 두 번 호출하고, `prepared_input` 대비 `first/mid frame` heuristic을 함께 기록합니다.
- 이번 실행은 Hugging Face retry 오염을 줄이기 위해 `--offline`으로 돌렸습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-44-local-ltx-video-camera-motion-ovaat/summary.json`
- `docs/experiments/artifacts/exp-44-local-ltx-video-camera-motion-ovaat/baseline-push-in/summary.json`
- `docs/experiments/artifacts/exp-44-local-ltx-video-camera-motion-ovaat/variant-static-close-up/summary.json`
- `docs/experiments/artifacts/exp-44-local-ltx-video-camera-motion-ovaat/baseline-push-in/ltx_first_try_mid_frame.png`
- `docs/experiments/artifacts/exp-44-local-ltx-video-camera-motion-ovaat/variant-static-close-up/ltx_first_try_mid_frame.png`

### baseline 대비 차이

- 실행 시간
  - baseline: `11.39초`
  - variant: `11.52초`
- mid frame heuristic
  - baseline MSE: `582.83`
  - variant MSE: `361.05`
  - baseline edge variance: `2053.80`
  - variant edge variance: `1856.82`
- 관찰
  - `slow push-in`은 접시 경계와 규카츠 결 주변의 잔상이 더 보였습니다.
  - `static close-up`은 접시/소스 칸 경계가 더 안정적이고 전체 음식 구조 붕괴가 덜했습니다.

### 확인된 것

1. 이번 샘플에서는 `camera motion phrase`가 실제 유효 레버였습니다.
2. `LTX`는 음식 컷에서 공격적인 카메라 지시보다 더 정적인 motion phrase에 안정적으로 반응했습니다.
3. 실행 시간 차이는 거의 없어서, 품질 기준으로 `static close-up`이 더 유리했습니다.

## 6. 실패/제약

1. 이번 판단은 단일 이미지 1장 기준입니다.
2. `static close-up`이 더 안정적이긴 했지만, clip 전체에서 지나치게 정적으로 보일 위험은 아직 따로 확인하지 않았습니다.
3. heuristic은 보조값이므로, 최종 판단은 육안 확인과 함께 봐야 합니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 현재 `LTX`에서 음식 구조 보존을 우선할 때는 `slow push-in`보다 `static close-up`이 더 적절합니다.
  - 다음 `LTX` 연구는 강한 카메라 연출보다 `미세한 motion phrase` 조합을 탐색하는 편이 낫습니다.

## 8. 다음 액션

1. 다음 OVAT는 `static close-up`을 유지한 채 `steam intensity` 또는 `micro camera movement`로 이어갑니다.
2. 본선 이식 전에는 실제 clip 전체 시청 기준으로 너무 정적이지 않은지 한 번 더 봐야 합니다.

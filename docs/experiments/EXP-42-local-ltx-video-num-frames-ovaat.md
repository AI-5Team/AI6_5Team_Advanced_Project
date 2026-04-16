# EXP-42 Local LTX-Video num_frames OVAT

## 1. 기본 정보

- 실험 ID: `EXP-42`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 이미지-투-비디오 파라미터 OVAT`

## 2. 왜 이 작업을 했는가

- `EXP-40`에서 `short prompt`가 현재 `LTX` baseline으로 더 적절하다는 점을 확인했습니다.
- 다음으로는 같은 prompt를 유지한 채 `num_frames`만 바꿨을 때 품질과 속도가 어떻게 달라지는지 봐야 했습니다.

## 3. baseline

### 고정한 조건

1. 하드웨어: `RTX 4080 SUPER 16GB / RAM 64GB`
2. 모델: `Lightricks/LTX-Video` + `city96/LTX-Video-gguf / ltx-video-2b-v0.9-Q3_K_S.gguf`
3. 입력 이미지: `docs/sample/음식사진샘플(규카츠).jpg`
4. prompt: `crispy gyukatsu, gentle steam, slow push-in, warm restaurant lighting, realistic food motion`
5. 설정: `6스텝 / 8fps / guidance 3.0 / seed 7`
6. 바뀐 변수: `num_frames`만 변경

### 비교 대상

- baseline: `17프레임`
- variant: `25프레임`

## 4. 무엇을 바꿨는가

- 재현용 스크립트 `scripts/local_video_ltx_num_frames_ovaat.py`를 추가했습니다.
- wrapper 스크립트는 `local_video_ltx_first_try.py`를 두 번 호출하고, `prepared_input` 대비 `first/mid frame`의 heuristic을 함께 기록합니다.
- 이번 실행은 Hugging Face HEAD retry 오염을 줄이기 위해 `--offline`으로 돌렸습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-42-local-ltx-video-num-frames-ovaat/summary.json`
- `docs/experiments/artifacts/exp-42-local-ltx-video-num-frames-ovaat/frames-17/summary.json`
- `docs/experiments/artifacts/exp-42-local-ltx-video-num-frames-ovaat/frames-25/summary.json`
- `docs/experiments/artifacts/exp-42-local-ltx-video-num-frames-ovaat/frames-17/ltx_first_try_mid_frame.png`
- `docs/experiments/artifacts/exp-42-local-ltx-video-num-frames-ovaat/frames-25/ltx_first_try_mid_frame.png`

### baseline 대비 차이

- 실행 시간
  - baseline: `11.52초`
  - variant: `11.72초`
- mid frame heuristic
  - baseline MSE: `318.92`
  - variant MSE: `280.42`
  - baseline edge variance: `1958.69`
  - variant edge variance: `2025.72`
- 관찰
  - `25프레임`은 실행 시간이 거의 늘지 않았습니다.
  - mid frame 기준으로는 `17프레임`보다 규카츠 표면과 접시 경계가 조금 더 안정적으로 보였습니다.

### 확인된 것

1. 현재 설정에서는 `25프레임`이 `17프레임`보다 나쁘지 않았고, 오히려 mid frame 품질은 약간 더 좋았습니다.
2. `num_frames`는 `steps`와 달리 실제로 다시 볼 가치가 있는 레버입니다.
3. 이 결과만 놓고 보면 현 하드웨어에서 `25프레임`도 충분히 실행 가능한 범위입니다.

## 6. 실패/제약

1. 이번 판단은 단일 이미지 1장 기준입니다.
2. heuristic은 보조 지표이므로, 최종 판단은 프레임 육안 확인과 함께 봐야 합니다.
3. 프레임 수가 늘어났을 때 clip 전체의 모션 자연스러움은 별도 평가가 더 필요합니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `num_frames`는 유효 레버 후보입니다.
  - 이번 샘플에서는 `25프레임`이 baseline보다 밀리지 않았고, 중간 프레임 품질은 오히려 조금 나았습니다.

## 8. 다음 액션

1. 다음 `LTX` OVAT는 `camera motion phrase`로 이어가는 편이 적절합니다.
2. `25프레임`을 유지할지 여부는 실제 clip 전체 움직임을 포함해 한 번 더 판단해야 합니다.

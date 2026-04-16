# EXP-37 Local LTX-Video 2B GGUF Steps OVAT

## 1. 기본 정보

- 실험 ID: `EXP-37`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 이미지-투-비디오 파라미터 OVAT`

## 2. 왜 이 작업을 했는가

- `EXP-36`에서 `LTX-Video 2B / GGUF`가 현재 장비에서 실제로 돌아간다는 것은 확인했습니다.
- 다음 단계는 모델을 바꾸기 전에, 가장 기본 파라미터인 `num_inference_steps`만 바꿨을 때 고스팅과 디테일 보존이 달라지는지 확인하는 것이었습니다.

## 3. baseline

### 고정한 조건

1. 하드웨어: `RTX 4080 SUPER 16GB / RAM 64GB`
2. 모델: `Lightricks/LTX-Video` + `city96/LTX-Video-gguf / ltx-video-2b-v0.9-Q3_K_S.gguf`
3. 입력 이미지: `docs/sample/음식사진샘플(규카츠).jpg`
4. 해상도/길이: `704x480 / 17프레임 / 8fps`
5. 프롬프트, seed, guidance_scale 고정
6. 바뀐 변수: `steps`만 변경

### 비교 대상

- baseline: `steps=6`
- variant: `steps=10`

## 4. 무엇을 바꿨는가

- 기존 `scripts/local_video_ltx_first_try.py`를 재사용
- 출력 디렉터리만 분리해 아래 두 조건을 실행
  - `steps=6`
  - `steps=10`

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-37-local-ltx-video-steps-ovaat/steps-6/summary.json`
- `docs/experiments/artifacts/exp-37-local-ltx-video-steps-ovaat/steps-10/summary.json`

### baseline 대비 차이

- `steps=6`
  - 실행 시간: `12.93초`
  - mid frame 입력 대비 MSE heuristic: `658.43`
  - 관찰: 약한 고스팅은 보이지만 음식 구조 보존은 비교적 안정적
- `steps=10`
  - 실행 시간: `13.44초`
  - mid frame 입력 대비 MSE heuristic: `890.95`
  - 관찰: 접시 하단과 우하단 국 그릇 쪽 잔상/고스팅이 더 커짐

### 확인된 것

1. 이번 조건에서는 `steps`를 `6 -> 10`으로 올려도 실행 시간 증가는 크지 않았습니다.
2. 하지만 시각적으로는 `steps=10`이 더 좋아지지 않았고, 오히려 고스팅이 약간 더 커졌습니다.
3. 현재 `LTX` baseline에서는 `steps`를 올리는 것보다 prompt 또는 frame count 쪽이 더 유의미한 다음 레버일 가능성이 높습니다.

## 6. 실패/제약

1. 이번 비교는 짧은 17프레임 smoke test라 절대 품질 실험은 아닙니다.
2. MSE/edge 지표는 관찰 보조용 heuristic일 뿐, 실제 영상 품질 점수는 아닙니다.
3. 단일 음식 사진 1장 기준이라 다른 메뉴 사진에서도 같은 경향이 유지되는지는 아직 모릅니다.

## 7. 결론

- 가설 충족 여부: **미충족**
- 판단:
  - `steps` 증가는 이번 설정에서 개선 레버가 아니었습니다.
  - `LTX`는 다음 OVAT를 `prompt length` 또는 `num_frames` 쪽으로 보는 편이 더 낫습니다.

## 8. 다음 액션

1. 다음은 `LTX`를 고정하고 `prompt length` 한 레버를 실험합니다.
2. 병렬 비교 후보로 `CogVideoX-5B-I2V` first try를 실제 실행합니다.

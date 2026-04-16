# EXP-38 Local CogVideoX-5B-I2V First Try

## 1. 기본 정보

- 실험 ID: `EXP-38`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 이미지-투-비디오 비교 후보 실행`

## 2. 왜 이 작업을 했는가

- `EXP-32`에서 `CogVideoX-5B-I2V`를 `LTX` 다음 비교 후보로 정리했습니다.
- 현재 장비에서 실제로 돌아가는지, 그리고 `LTX`와 비교해 첫 인상이 어떤지를 확인할 필요가 있었습니다.

## 3. baseline

### 고정한 조건

1. 하드웨어: `RTX 4080 SUPER 16GB / RAM 64GB`
2. 모델: `THUDM/CogVideoX-5b-I2V`
3. 입력 이미지: `docs/sample/음식사진샘플(규카츠).jpg`
4. 해상도/길이: `720x480 / 16프레임 / 8fps`
5. 설정: `steps=8`, `guidance_scale=6.0`, `enable_model_cpu_offload`, `VAE slicing/tiling`

## 4. 무엇을 바꿨는가

- `scripts/local_video_cogvideox_first_try.py` 추가
  - `CogVideoXImageToVideoPipeline` 기반 최소 I2V smoke test
  - `prepared_input`, `first_frame`, `mid_frame`, `mp4`, `summary.json` 저장
  - repo `.env.local` 자동 로드

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-38-local-cogvideox-first-try/summary.json`
- `docs/experiments/artifacts/exp-38-local-cogvideox-first-try/cogvideox_first_try.mp4`
- `docs/experiments/artifacts/exp-38-local-cogvideox-first-try/cogvideox_first_try_first_frame.png`
- `docs/experiments/artifacts/exp-38-local-cogvideox-first-try/cogvideox_first_try_mid_frame.png`

### 확인된 것

1. `CogVideoX-5B-I2V`는 현재 장비에서 실제 1회 실행이 가능합니다.
2. 하지만 first try 품질은 현재 `LTX`보다 훨씬 약했습니다.
3. 첫 프레임부터 격자형/모자이크성 artifact가 강하게 보였고, 중간 프레임도 음식 디테일 보존이 좋지 않았습니다.
4. 실행 시간은 `353.29초`로 `LTX`보다 훨씬 길었습니다.

## 6. 실패/제약

1. 실행은 성공했지만, 현재 설정에서는 결과 품질이 baseline 후보라고 보기 어렵습니다.
2. 첫 실행에 model download 시간이 많이 포함됐습니다.
3. Windows Hugging Face symlink warning이 있었지만 실행 자체는 막지 않았습니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `실행 가능성`은 확인됐습니다.
  - 하지만 `현재 first try 품질/속도` 기준으로는 `LTX`가 우선입니다.
  - `CogVideoX`는 버릴 카드는 아니지만, 지금 당장 주력 baseline lane은 아닙니다.

## 8. 다음 액션

1. 비디오 baseline lane은 계속 `LTX`를 우선합니다.
2. `CogVideoX`는 나중에 프레임 수/steps/CFG를 다시 조정해 재시도할 수 있습니다.
3. 다음 즉시 레버는 `LTX prompt length` 또는 `LTX num_frames`입니다.

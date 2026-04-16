# EXP-36 Local LTX-Video 2B GGUF First Try

## 1. 기본 정보

- 실험 ID: `EXP-36`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 이미지-투-비디오 실행`

## 2. 왜 이 작업을 했는가

- `EXP-34`는 preflight까지만 확인했고, 아직 실제 비디오 생성은 하지 못했습니다.
- 현재 장비에서 `Wan2.2-I2V-A14B`, `LTX-2.3`보다 먼저 볼 후보를 `LTX-Video 2B / GGUF`로 정리했기 때문에, 실제 1회 생성이 가능한지 확인할 필요가 있었습니다.

## 3. baseline

### 고정한 조건

1. 하드웨어: `RTX 4080 SUPER 16GB / RAM 64GB`
2. base repo: `Lightricks/LTX-Video`
3. GGUF: `city96/LTX-Video-gguf / ltx-video-2b-v0.9-Q3_K_S.gguf`
4. 입력 이미지: `docs/sample/음식사진샘플(규카츠).jpg`
5. 출력 목표: 아주 짧은 `17프레임 / 6스텝 / 8fps` first try

## 4. 무엇을 바꿨는가

- `scripts/local_video_ltx_first_try.py`
  - repo `.env.local`을 읽고 Hugging Face cache를 사용할 수 있게 구성
  - `hf_hub_download()`로 GGUF 파일을 내려받고 `LTXImageToVideoPipeline`으로 I2V 실행
  - `prepared_input.png`, `first_frame`, `mid_frame`, `mp4`, `summary.json`을 artifact로 저장
- 시스템 Python GPU 환경에 아래 패키지를 추가
  - `diffusers==0.37.1`
  - `sentencepiece`
  - `imageio-ffmpeg`
  - `gguf>=0.10.0`

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-36-local-ltx-video-first-try/summary.json`
- `docs/experiments/artifacts/exp-36-local-ltx-video-first-try/ltx_first_try.mp4`
- `docs/experiments/artifacts/exp-36-local-ltx-video-first-try/ltx_first_try_first_frame.png`
- `docs/experiments/artifacts/exp-36-local-ltx-video-first-try/ltx_first_try_mid_frame.png`

### 확인된 것

1. `LTX-Video 2B / GGUF`는 현재 로컬 장비에서 실제 1회 생성이 됩니다.
2. warm cache 기준 실행 시간은 `12.6초`였습니다.
3. 첫 프레임은 규카츠 플레이팅과 조명 정보가 비교적 잘 유지됐습니다.
4. 중간 프레임에서는 약한 고스팅과 소프트 블러가 보여, 실행 성공과 baseline-ready 품질은 아직 다릅니다.

## 6. 실패/제약

1. 첫 실행 전 두 번의 blocker가 있었습니다.
   - GGUF URL 직접 전달 실패
   - `gguf` 패키지 미설치
2. Windows에서 Hugging Face symlink warning이 나왔지만 실행 자체를 막지는 않았습니다.
3. 이번 결과는 `first try`이므로, 아직 motion quality나 음식 디테일 보존을 충분히 평가한 건 아닙니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `LTX-Video 2B / GGUF`는 현재 장비에서 실제 로컬 비디오 baseline 후보가 됩니다.
  - 다만 품질은 아직 약간 흐리고 고스팅이 보여, 다음 단계는 모델 변경보다 `steps / frame count / prompt` 같은 기본 파라미터 OVAT가 먼저입니다.

## 8. 다음 액션

1. 다음은 같은 모델을 고정하고 `steps` 또는 `prompt length` 한 레버만 바꿔 품질 변화를 봅니다.
2. 그 다음 로컬 비디오 비교 후보로 `CogVideoX-5B-I2V` first try를 붙입니다.
3. `Wan2.2-I2V-A14B`, `LTX-2.3`는 현재 장비 baseline lane에 바로 올리기보다 나중 후보로 둡니다.

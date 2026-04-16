# EXP-40 Local LTX-Video Prompt Length OVAT

## 1. 기본 정보

- 실험 ID: `EXP-40`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 이미지-투-비디오 파라미터 OVAT`

## 2. 왜 이 작업을 했는가

- `EXP-37`에서 `steps`는 유효 레버가 아니었습니다.
- 따라서 같은 `LTX-Video 2B / GGUF`를 고정한 채, 이번에는 `prompt length`만 바꿨을 때 음식 구조 보존과 고스팅이 달라지는지 확인했습니다.

## 3. baseline

### 고정한 조건

1. 하드웨어: `RTX 4080 SUPER 16GB / RAM 64GB`
2. 모델: `Lightricks/LTX-Video` + `city96/LTX-Video-gguf / ltx-video-2b-v0.9-Q3_K_S.gguf`
3. 입력 이미지: `docs/sample/음식사진샘플(규카츠).jpg`
4. 설정: `17프레임 / 6스텝 / 8fps / guidance 3.0 / seed 7`
5. 바뀐 변수: `prompt length`만 변경

### 비교 대상

- baseline: default prompt
- variant: short prompt

## 4. 무엇을 바꿨는가

- 기존 `scripts/local_video_ltx_first_try.py`를 재사용
- prompt만 아래처럼 변경
  - baseline: 긴 설명형 prompt
  - variant: `crispy gyukatsu, gentle steam, slow push-in, warm restaurant lighting, realistic food motion`

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-40-local-ltx-video-prompt-length-ovaat/default-prompt/summary.json`
- `docs/experiments/artifacts/exp-40-local-ltx-video-prompt-length-ovaat/short-prompt/summary.json`
- `docs/experiments/artifacts/exp-40-local-ltx-video-prompt-length-ovaat/default-prompt-warm/summary.json`
- `docs/experiments/artifacts/exp-40-local-ltx-video-prompt-length-ovaat/short-prompt-warm/summary.json`

### baseline 대비 차이

- warm cache 기준 실행 시간
  - baseline: `11.07초`
  - variant: `10.94초`
- mid frame heuristic
  - baseline MSE: `658.43`
  - variant MSE: `318.92`
- 관찰
  - baseline은 좌측 규카츠와 하단 소스 트레이 쪽 잔상이 비교적 큽니다.
  - variant는 같은 프레임에서 음식 구조와 접시 경계가 더 잘 유지됩니다.

### 확인된 것

1. 이번 설정에서는 `short prompt`가 `default prompt`보다 더 나았습니다.
2. 속도 차이는 거의 없었고, 품질 쪽에서 차이가 더 분명했습니다.
3. `LTX`는 설명을 길게 주기보다 짧고 직접적인 음식/카메라/조명 키워드가 더 안정적인 경향을 보였습니다.

## 6. 실패/제약

1. 첫 `short prompt` 실행은 Hugging Face HEAD retry 때문에 latency가 오염됐습니다.
2. 그래서 warm cache 실행을 별도로 다시 돌려 비교했습니다.
3. 이번 판단은 단일 이미지 1장 기준입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 현재 `LTX`에서는 `prompt length`가 실제 유효 레버입니다.
  - 다음 OVAT는 `num_frames` 또는 `guidance_scale`보다, 먼저 `prompt phrasing` 세분화가 더 가치 있습니다.

## 8. 다음 액션

1. 다음 `LTX` 연구는 `short prompt`를 baseline으로 유지합니다.
2. 그다음 레버는 `num_frames` 또는 `camera motion phrase` 중 하나로 분리합니다.

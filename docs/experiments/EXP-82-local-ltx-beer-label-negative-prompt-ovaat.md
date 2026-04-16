# EXP-82 Local LTX beer label negative prompt OVAT

## 1. 기본 정보

- 실험 ID: `EXP-82`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / beer lane 후속 레버`

## 2. 왜 이 작업을 했는가

- 현재 global negative prompt에는 `text, watermark`가 포함되어 있습니다.
- 이 항목이 `맥주` bottle label 같은 실제 텍스트 요소를 해칠 가능성이 있어, baseline prompt는 고정한 채 negative prompt에서 `text, watermark`만 제거하는 OVAT를 진행했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. 이미지: `맥주`
4. prepare mode: `auto` (`resolved_prepare_mode = cover_top`)
5. prompt: `still life beverage shot` baseline 유지
6. frames / steps / fps: `25 / 6 / 8`

### 이번에 바꾼 레버

- `negative prompt`만 바꿨습니다.
- baseline:
  - `worst quality, blurry, jittery, distorted, warped, overexposed, text, watermark`
- variant:
  - `worst quality, blurry, jittery, distorted, warped, overexposed`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_beer_label_negative_prompt_ovaat.py`
   - baseline negative prompt와 `text/watermark` 제거 variant를 비교하는 OVAT 스크립트를 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-82-local-ltx-beer-label-negative-prompt-ovaat/summary.json`

### aggregate

- baseline mid-frame MSE: `268.79`
- variant mid-frame MSE: `354.10`
- mid-frame MSE delta: `-85.31`
- edge variance delta: `+13.50`

### 확인된 것

1. `text, watermark`를 제거한 variant는 오히려 `mid-frame MSE`가 나빠졌습니다.
2. 실제 frame도 baseline보다 bottle/glass 전체 구조가 더 안정적이라고 보기 어려웠습니다.
3. 따라서 현재 조건에서는 `text/watermark` 제거가 label 보존 해결책이 아니었습니다.

## 6. 실패/제약

1. `맥주` 1장 기준입니다.
2. `edge variance`는 소폭 좋아졌지만, 핵심 지표인 전체 구조 안정성은 오히려 악화됐습니다.

## 7. 결론

- 가설 충족 여부: **실패**
- 판단:
  - `negative prompt`에서 `text, watermark`를 빼는 방향은 현재 baseline lane에 맞지 않습니다.
  - global negative prompt는 그대로 유지하는 편이 맞습니다.

## 8. 다음 액션

1. `맥주` label 문제는 negative prompt보다 다른 입력 레버를 보는 편이 맞습니다.
2. 다음은 label area를 더 크게 보이게 하는 crop/prepare-mode 보조 전략이나 bottle-centered framing 쪽을 검토할 수 있습니다.

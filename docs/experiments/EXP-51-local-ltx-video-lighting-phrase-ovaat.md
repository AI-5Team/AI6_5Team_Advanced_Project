# EXP-51 Local LTX-Video lighting phrase OVAT

## 1. 기본 정보

- 실험 ID: `EXP-51`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 이미지-투-비디오 프롬프트 OVAT`

## 2. 왜 이 작업을 했는가

- `EXP-48`에서 `strong steam cloud`가 의외로 음식 구조를 망치지 않고 오히려 더 나았습니다.
- 다음으로는 음식컷에서 자주 같이 붙는 `lighting phrase`만 바꿨을 때 품질이 어떻게 달라지는지 확인할 필요가 있었습니다.

## 3. baseline

### 고정한 조건

1. 하드웨어: `RTX 4080 SUPER 16GB / RAM 64GB`
2. 모델: `Lightricks/LTX-Video` + `city96/LTX-Video-gguf / ltx-video-2b-v0.9-Q3_K_S.gguf`
3. 입력 이미지: `docs/sample/음식사진샘플(규카츠).jpg`
4. 설정: `25프레임 / 6스텝 / 8fps / guidance 3.0 / seed 7`
5. 공통 prompt suffix: `strong steam cloud, realistic food motion, static close-up, minimal camera movement`
6. 바뀐 변수: `lighting phrase`만 변경

### 비교 대상

- baseline: `warm restaurant lighting`
- variant: `bright tabletop lighting`

## 4. 무엇을 바꿨는가

- 재현용 스크립트 `scripts/local_video_ltx_lighting_ovaat.py`를 추가했습니다.
- `local_video_ltx_first_try.py`를 두 번 호출해 `first/mid frame` heuristic을 함께 기록했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-51-local-ltx-video-lighting-phrase-ovaat/summary.json`
- `docs/experiments/artifacts/exp-51-local-ltx-video-lighting-phrase-ovaat/baseline-warm-lighting/ltx_first_try_mid_frame.png`
- `docs/experiments/artifacts/exp-51-local-ltx-video-lighting-phrase-ovaat/variant-bright-lighting/ltx_first_try_mid_frame.png`

### baseline 대비 차이

- 실행 시간
  - baseline: `12.20초`
  - variant: `11.64초`
- mid frame heuristic
  - baseline MSE: `298.65`
  - variant MSE: `246.90`
  - baseline edge variance: `1845.25`
  - variant edge variance: `1952.13`
- 관찰
  - `bright tabletop lighting` 쪽이 규카츠 결, 소스 칸 경계, 접시 윤곽이 조금 더 또렷했습니다.
  - `warm restaurant lighting`은 전체 톤은 자연스럽지만 mid frame에서 살짝 더 흐려졌습니다.

### 확인된 것

1. 이번 샘플에서는 `lighting phrase`도 유효 레버였습니다.
2. `bright tabletop lighting`이 더 밝다고 해서 음식 구조가 망가지지는 않았습니다.
3. 현재 `LTX` food shot baseline은 `strong steam cloud + static close-up` 위에 `bright tabletop lighting`까지 포함하는 편이 유리해 보입니다.

## 6. 실패/제약

1. 이번 판단은 단일 이미지 1장 기준입니다.
2. 너무 밝은 조명 표현이 다른 음식에서는 과한 하이라이트를 만들 가능성이 있습니다.
3. frame heuristic은 좋아졌지만 clip 전체 리듬까지 본 것은 아닙니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 이번 샘플에서는 `bright tabletop lighting`이 baseline보다 낫습니다.
  - 다음 LTX 레버는 `texture emphasis` 또는 `food motion phrase`를 보는 편이 적절합니다.

## 8. 다음 액션

1. 다음 OVAT는 `texture emphasis` 또는 `food motion phrase`로 이어갑니다.
2. `bright tabletop lighting`은 다른 음식 샘플 1~2개에 대해서도 재현성을 확인해야 합니다.

# EXP-48 Local LTX-Video steam intensity OVAT

## 1. 기본 정보

- 실험 ID: `EXP-48`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 이미지-투-비디오 프롬프트 OVAT`

## 2. 왜 이 작업을 했는가

- `EXP-46`까지 진행한 결과 현재 `LTX` baseline은 `static close-up, minimal camera movement`를 유지하는 편이 맞았습니다.
- 다음으로는 음식컷에서 자주 쓰는 표현인 `steam intensity`만 바꿨을 때 품질이 달라지는지 확인해야 했습니다.

## 3. baseline

### 고정한 조건

1. 하드웨어: `RTX 4080 SUPER 16GB / RAM 64GB`
2. 모델: `Lightricks/LTX-Video` + `city96/LTX-Video-gguf / ltx-video-2b-v0.9-Q3_K_S.gguf`
3. 입력 이미지: `docs/sample/음식사진샘플(규카츠).jpg`
4. 설정: `25프레임 / 6스텝 / 8fps / guidance 3.0 / seed 7`
5. 공통 prompt suffix: `warm restaurant lighting, realistic food motion, static close-up, minimal camera movement`
6. 바뀐 변수: `steam intensity`만 변경

### 비교 대상

- baseline: `gentle steam`
- variant: `strong steam cloud`

## 4. 무엇을 바꿨는가

- 재현용 스크립트 `scripts/local_video_ltx_steam_ovaat.py`를 추가했습니다.
- `local_video_ltx_first_try.py`를 두 번 호출해 `prepared_input` 대비 `first/mid frame` heuristic을 함께 기록했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-48-local-ltx-video-steam-intensity-ovaat/summary.json`
- `docs/experiments/artifacts/exp-48-local-ltx-video-steam-intensity-ovaat/baseline-gentle-steam/ltx_first_try_mid_frame.png`
- `docs/experiments/artifacts/exp-48-local-ltx-video-steam-intensity-ovaat/variant-strong-steam/ltx_first_try_mid_frame.png`

### baseline 대비 차이

- 실행 시간
  - baseline: `11.72초`
  - variant: `11.52초`
- mid frame heuristic
  - baseline MSE: `361.05`
  - variant MSE: `234.38`
  - baseline edge variance: `1856.82`
  - variant edge variance: `2004.31`
- 관찰
  - `strong steam cloud`가 의외로 음식 구조를 더 망치지 않았습니다.
  - mid frame 기준으로는 규카츠 결, 접시 경계, 소스 칸 윤곽이 baseline보다 조금 더 선명했습니다.

### 확인된 것

1. 이번 샘플에서는 `steam intensity`가 실제 유효 레버였습니다.
2. `strong steam cloud`가 단순히 artifact를 늘릴 것이라는 가설은 맞지 않았습니다.
3. 현재 `LTX` food shot에서는 `steam`을 너무 보수적으로 줄일 필요는 없습니다.

## 6. 실패/제약

1. 이번 판단은 단일 이미지 1장 기준입니다.
2. `strong steam cloud`가 다른 음식 사진에서도 일관되게 좋은지는 아직 모릅니다.
3. clip 전체 움직임 기준으로 과한 연기가 느껴지는지는 추가 확인이 필요합니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 이번 샘플에서는 `strong steam cloud`가 baseline보다 낫습니다.
  - 다음 LTX 레버는 `lighting phrase`를 보는 편이 적절합니다.

## 8. 다음 액션

1. 다음 OVAT는 `lighting phrase` 또는 `food texture emphasis`로 이어갑니다.
2. `steam` 표현은 다른 음식 샘플 1~2개에 대해서도 재현성을 확인해야 합니다.

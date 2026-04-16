# EXP-61 Local LTX seed stability

## 1. 기본 정보

- 실험 ID: `EXP-61`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / LTX seed 안정성`

## 2. 왜 이 작업을 했는가

- `EXP-58`에서 현재 LTX baseline이 음식군 전반으로 일반화되지 않는다는 점은 확인됐습니다.
- 그 전에 같은 음식 사진 하나에서도 결과가 seed에 따라 얼마나 흔들리는지 먼저 봐야 했습니다.
- prompt phrasing 레버가 거의 소진된 상태라, 재현성 자체가 더 큰 병목인지 점검할 필요가 있었습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. 이미지: `docs/sample/음식사진샘플(규카츠).jpg`
3. prompt: `crispy gyukatsu, bright tabletop lighting, strong steam cloud, realistic food motion, static close-up, minimal camera movement`
4. negative prompt: 기본값
5. frames / steps / fps: `25 / 6 / 8`

### 이번에 바꾼 레버

- `seed`만 바꿨습니다.
- 비교 seed: `7`, `11`, `19`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_seed_stability.py`를 추가했습니다.
2. 각 seed를 같은 baseline 조건으로 실행하고,
   - input 대비 mid-frame MSE
   - mid-frame edge variance
   - seed 간 pairwise mid-frame MSE
   를 함께 기록하도록 했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-61-local-ltx-seed-stability/summary.json`

### seed별 결과

1. seed `7`
   - mid-frame MSE: `246.90`
   - edge variance: `1952.13`
2. seed `11`
   - mid-frame MSE: `490.31`
   - edge variance: `1689.08`
3. seed `19`
   - mid-frame MSE: `578.85`
   - edge variance: `1470.54`

### baseline 대비 차이

- 최고 seed(`7`)와 최악 seed(`19`)의 mid-frame MSE 차이는 `331.95`였습니다.
- seed 간 평균 pairwise mid-frame MSE는 `346.81`이었습니다.
- mid-frame MSE 표준편차는 `140.35`로 꽤 컸습니다.

### 확인된 것

1. 현재 LTX baseline은 seed 민감도가 큽니다.
2. 같은 규카츠 이미지라도 seed가 바뀌면 중간 프레임 품질이 크게 달라집니다.
3. 따라서 지금은 prompt 문구를 더 깎는 것보다 seed 전략이나 multi-seed shortlist가 더 중요합니다.

## 6. 실패/제약

1. 이번 실험은 규카츠 1장 기준입니다.
2. 수치와 함께 시각 확인도 했지만, 아직 사람 평가 표본은 없습니다.
3. seed를 3개만 봤기 때문에 분포 전체를 대표한다고 보긴 어렵습니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 현재 baseline은 seed에 따라 결과 흔들림이 큽니다.
  - 음식군 일반화 전에 seed 전략을 먼저 정리하는 편이 맞습니다.

## 8. 다음 액션

1. 규카츠 baseline에서 `multi-seed shortlist` 전략을 검토합니다.
2. 또는 음식군별 baseline prompt를 나눠서 seed 민감도가 줄어드는지 확인합니다.

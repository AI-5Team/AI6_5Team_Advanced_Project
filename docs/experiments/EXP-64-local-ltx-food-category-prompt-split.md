# EXP-64 Local LTX food-category prompt split

## 1. 기본 정보

- 실험 ID: `EXP-64`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / generic prompt vs 음식군별 tailored prompt`

## 2. 왜 이 작업을 했는가

- `EXP-63`에서 `multi-seed shortlist`는 강한 해법이 아니라는 점이 확인됐습니다.
- 다음 가설은 `seed`보다 `음식군별 baseline prompt 분리`가 더 큰 레버일 수 있다는 것이었습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. negative prompt: 기본값
4. frames / steps / fps: `25 / 6 / 8`
5. 이미지:
   - `규카츠`
   - `라멘`
   - `순두부짬뽕`
   - `장어덮밥`
   - `커피`
   - `아이스크림`

### 이번에 바꾼 레버

- `prompt template family`만 바꿨습니다.
- baseline: 음식 라벨 + 공통 baseline prompt
- variant: 음식군별 tailored prompt

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_food_category_prompt_split.py`를 추가했습니다.
2. 각 이미지에 대해 다음 두 가지를 비교했습니다.
   - generic prompt
   - tailored food-category prompt

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-64-local-ltx-food-category-prompt-split/summary.json`

### 이미지별 결과

1. 규카츠
   - generic mid-frame MSE: `246.90`
   - tailored mid-frame MSE: `205.30`
   - improvement: `+41.60`
2. 라멘
   - generic: `720.39`
   - tailored: `1154.45`
   - improvement: `-434.06`
3. 순두부짬뽕
   - generic: `596.56`
   - tailored: `609.08`
   - improvement: `-12.52`
4. 장어덮밥
   - generic: `924.08`
   - tailored: `1915.21`
   - improvement: `-991.13`
5. 커피
   - generic: `169.43`
   - tailored: `161.89`
   - improvement: `+7.54`
6. 아이스크림
   - generic: `76.97`
   - tailored: `97.35`
   - improvement: `-20.38`

### aggregate

- tailored prompt가 실제로 나아진 이미지는 `6개 중 2개`였습니다.
- average mid-frame MSE delta는 `-234.83`이었습니다.
- average edge variance delta는 `-44.55`였습니다.

### 확인된 것

1. naive한 음식군별 prompt 분리는 전반적 개선으로 이어지지 않았습니다.
2. 규카츠와 커피에서는 도움됐습니다.
3. 라멘과 장어덮밥에서는 오히려 크게 악화됐습니다.
4. 따라서 현재 병목은 단순한 음식명 기반 분기보다 더 세밀한 `구도/표면/질감` 분류에 가깝습니다.

## 6. 실패/제약

1. tailored prompt는 수작업 1차안이라 설계 품질 한계가 있습니다.
2. 이번 실험은 seed `7` 고정 기준입니다.
3. `장어덮밥`처럼 tailored prompt가 심하게 망가지는 케이스가 있었습니다.

## 7. 결론

- 가설 충족 여부: **기각**
- 판단:
  - `음식군별 prompt 분리`를 지금 형태로 바로 baseline 전략으로 쓰는 것은 맞지 않습니다.
  - generic baseline을 유지한 채 더 정교한 분류 축을 찾아야 합니다.

## 8. 다음 액션

1. 다음 레버는 `음식군`보다 `구도/촬영 타입` 분류가 더 적절한지 확인합니다.
2. 특히 `overhead bowl`, `tray set`, `glass drink`, `dessert close-up`처럼 시각 구도 중심 분기가 더 유력합니다.

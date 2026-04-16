# EXP-63 Local LTX multi-seed shortlist

## 1. 기본 정보

- 실험 ID: `EXP-63`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / fixed seed vs multi-seed shortlist`

## 2. 왜 이 작업을 했는가

- `EXP-61`에서 현재 LTX baseline이 seed 민감도가 크다는 점을 확인했습니다.
- 그래서 다음 질문은 단순합니다. `고정 seed 1개`보다 `짧은 seed shortlist`를 돌려 best seed를 고르는 전략이 실제로 도움이 되는가입니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. prompt shape: 음식군 라벨 + `bright tabletop lighting + strong steam cloud + realistic food motion + static close-up`
3. negative prompt: 기본값
4. frames / steps / fps: `25 / 6 / 8`
5. 이미지:
   - `규카츠`
   - `라멘`
   - `순두부짬뽕`
   - `장어덮밥`

### 이번에 바꾼 레버

- `seed strategy`만 바꿨습니다.
- baseline: fixed seed `7`
- variant: shortlist `7 / 11 / 19` 중 input 대비 mid-frame MSE가 가장 낮은 seed 선택

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_multi_seed_shortlist.py`를 추가했습니다.
2. 각 이미지에 대해 같은 prompt 조건으로 seed `7 / 11 / 19`를 모두 실행했습니다.
3. fixed seed `7`과 shortlist best seed를 비교했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-63-local-ltx-multi-seed-shortlist/summary.json`

### 이미지별 결과

1. 규카츠
   - fixed seed `7`이 이미 best였습니다.
   - improvement: `0.00`
2. 라멘
   - shortlist에서도 fixed seed `7`이 best였습니다.
   - improvement: `0.00`
3. 순두부짬뽕
   - fixed seed `7` → shortlist best seed `19`
   - mid-frame MSE: `596.56 -> 548.23`
   - improvement: `48.33`
4. 장어덮밥
   - fixed seed `7`이 best였습니다.
   - improvement: `0.00`

### aggregate

- shortlist가 실제로 나아진 이미지는 `4개 중 1개`였습니다.
- average mid-frame MSE delta는 `12.08`이었습니다.
- average edge variance delta는 `-25.13`으로 오히려 약간 나빠졌습니다.

### 확인된 것

1. shortlist 전략은 일부 이미지에선 도움되지만, 현재 seed 후보 `7 / 11 / 19`만으로는 강한 일반 해법이 아닙니다.
2. 규카츠/라멘/장어덮밥에서는 fixed seed `7`이 그대로 최선이었습니다.
3. 현재 병목은 `seed strategy` 하나만으로 해결되는 수준이 아니라 음식군별 baseline 품질 자체에 더 가깝습니다.

## 6. 실패/제약

1. shortlist oracle로 `input 대비 mid-frame MSE`를 썼기 때문에 제품 실시간 전략으로 바로 쓰긴 어렵습니다.
2. seed 후보를 3개만 썼습니다.
3. 순두부짬뽕은 수치 개선이 있었지만, edge variance는 더 낮아졌습니다.

## 7. 결론

- 가설 충족 여부: **부분 충족**
- 판단:
  - `multi-seed shortlist`는 완전히 무의미하진 않지만, 지금 단계의 우선 해결책은 아닙니다.
  - `음식군별 prompt template 분리`가 더 강한 후보로 올라옵니다.

## 8. 다음 액션

1. 라멘/국물류와 튀김류를 분리한 baseline prompt를 먼저 시도합니다.
2. shortlist는 그 다음 보조 전략으로만 재검토하는 편이 맞습니다.

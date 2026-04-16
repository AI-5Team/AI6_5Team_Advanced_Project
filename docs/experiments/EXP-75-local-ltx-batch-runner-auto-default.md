# EXP-75 Local LTX batch runner auto default

## 1. 기본 정보

- 실험 ID: `EXP-75`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / reusable batch runner`

## 2. 왜 이 작업을 했는가

- `EXP-73`으로 `prepare_mode auto`가 batch validation에서도 유지된다는 점은 확인했습니다.
- 하지만 그 경로는 여전히 experiment 전용 스크립트였고, 재사용 가능한 batch runner로 승격되진 않았습니다.
- 그래서 이번에는 실험 전용이 아닌 `local_video_ltx_batch_runner.py`를 추가하고, 기본값을 `--prepare-mode auto`로 둔 상태에서 대표 샘플 세트를 직접 실행했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. batch runner 기본값:
   - `prepare_mode = auto`
4. negative prompt: 기본값
5. frames / steps / fps: `25 / 6 / 8`
6. 대표 샘플:
   - `규카츠`
   - `라멘`
   - `순두부짬뽕`
   - `장어덮밥`
   - `커피`
   - `맥주`

### 이번에 바꾼 레버

- `batch runner default path`만 바꿨습니다.
- 실험 전용 validation 스크립트 대신 reusable runner를 기본값 `auto`로 실행했습니다.

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_batch_runner.py`
   - `--prepare-mode auto`를 기본값으로 하는 재사용 가능한 batch runner를 추가했습니다.
   - `--images`, `--prepare-mode` CLI 옵션을 열어 실험/운영 겸용으로 쓸 수 있게 했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-75-local-ltx-batch-runner-auto-default/summary.json`

### aggregate

- completed: `6 / 6`
- average elapsed seconds: `11.39`
- average mid-frame MSE: `335.96`

### 분기 결과

- `cover_center`: `1`
- `contain_blur`: `3`
- `cover_top`: `2`

### 확인된 것

1. reusable batch runner에서도 `auto`가 그대로 동작했습니다.
2. `커피`, `맥주`는 `cover_top`으로, `규카츠`는 `cover_center`로, 나머지는 `contain_blur`로 분기됐습니다.
3. 즉 prepare_mode baseline은 이제 experiment runner가 아니라 reusable runner 수준으로 승격됐습니다.

## 6. 실패/제약

1. `맥주`는 여전히 품질 metric이 높은 편이라, runner 안정성과 생성 품질은 별개 문제입니다.
2. 현재 runner는 prompt family를 단순 라벨 매핑으로 넣고 있어, 샘플별 prompt refinement는 별도 레이어입니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `prepare_mode auto`는 이제 batch runner 기본값으로 써도 됩니다.
  - 이후 실험은 runner를 또 바꾸기보다 샘플별 품질 레버를 보는 쪽이 맞습니다.

## 8. 다음 액션

1. 다음은 `규카츠 vs 타코야키`처럼 같은 tray/full-plate 안에서도 subtype별 prompt family를 나누는 것입니다.
2. drink 쪽은 `cover_top`을 유지하되, `맥주` 전용 후속 레버를 따로 보는 편이 맞습니다.

# EXP-72 Local LTX auto prepare_mode parity

## 1. 기본 정보

- 실험 ID: `EXP-72`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / actual generation runner auto prepare_mode 연결`

## 2. 왜 이 작업을 했는가

- `EXP-71`까지로 auto classifier v2 정책은 정리됐지만, 아직 실제 생성 경로에서는 수동 `prepare_mode`를 넣는 방식이었습니다.
- 따라서 이번에는 classifier v2를 `local_video_ltx_first_try.py`에 직접 연결하고, `manual policy`와 `auto policy`가 실제 생성 경로에서 완전히 같은 prepare_mode를 고르는지 확인했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. 이미지:
   - `규카츠`
   - `라멘`
   - `순두부짬뽕`
   - `장어덮밥`
   - `커피`
   - `맥주`
   - `아이스크림`
4. manual policy:
   - `규카츠`: `cover_center`
   - `라멘`: `contain_blur`
   - `순두부짬뽕`: `contain_blur`
   - `장어덮밥`: `contain_blur`
   - `커피`: `cover_top`
   - `맥주`: `cover_top`
   - `아이스크림`: `contain_blur`

### 이번에 바꾼 레버

- `prepare_mode selection path`만 바꿨습니다.
- baseline: 수동 `prepare_mode`
- variant: `--prepare-mode auto`

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_first_try.py`
   - `--prepare-mode auto`를 추가했습니다.
   - artifact에 `resolved_prepare_mode`, `auto_shot_type`, `structure_features`를 기록하도록 확장했습니다.
2. `scripts/local_video_ltx_auto_prepare_mode_parity.py`
   - manual policy와 auto policy를 같은 seed로 비교하는 parity 스크립트를 추가했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-72-local-ltx-auto-prepare-mode-parity/summary.json`

### aggregate

- image count: `7`
- matched count: `7`
- parity accuracy: `1.0`

### 확인된 것

1. `auto`는 7장 모두에서 수동 정책과 같은 `resolved_prepare_mode`를 골랐습니다.
2. `커피`, `맥주`는 모두 `glass_drink_candidate -> cover_top`으로 들어갔습니다.
3. 즉 이제 prepare_mode baseline은 manual override 없이도 실제 generation runner에서 재현됩니다.

## 6. 실패/제약

1. 현재 parity는 single-photo 샘플 7장 기준입니다.
2. classifier 자체는 여전히 heuristic이라 샘플이 더 늘어나면 다시 보정이 필요할 수 있습니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - prepare_mode baseline은 이제 실험 메모 수준이 아니라 실제 runner 옵션으로 승격할 수 있습니다.
  - current runner baseline은 `--prepare-mode auto`를 기본 후보로 볼 수 있습니다.

## 8. 다음 액션

1. 다음은 multi-image validation이나 후속 batch runner에서 `auto`를 기본값으로 쓰는 것입니다.
2. 이후 레버는 prompt보다 `shot type classifier`의 일반화 검증이 우선입니다.

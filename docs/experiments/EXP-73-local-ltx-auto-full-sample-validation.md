# EXP-73 Local LTX auto full sample validation

## 1. 기본 정보

- 실험 ID: `EXP-73`
- 작성일: `2026-04-09`
- 작성자: Codex
- 관련 기능: `로컬 비디오 연구선 / batch path auto prepare_mode validation`

## 2. 왜 이 작업을 했는가

- `EXP-72`에서 `prepare_mode auto`는 수동 policy 7장과 parity를 보였습니다.
- 하지만 그 검증은 known baseline set에 한정돼 있었고, 아직 전체 샘플 라이브러리에서 `auto`를 기본값처럼 썼을 때 분기와 품질이 유지되는지는 확인하지 않았습니다.
- 그래서 이번에는 `docs/sample`의 음식 사진 전체 11장에 `auto`를 태우는 batch validation을 별도로 실행했습니다.

## 3. baseline

### 고정한 조건

1. 모델: `LTX-Video 2B / GGUF`
2. seed: `7`
3. prepare mode: `auto`
4. negative prompt: 기본값
5. frames / steps / fps: `25 / 6 / 8`
6. 이미지:
   - `규카츠`
   - `귤모찌`
   - `라멘`
   - `맥주`
   - `순두부짬뽕`
   - `아이스크림`
   - `장어덮밥`
   - `초코소보로호두과자`
   - `카오위`
   - `커피`
   - `타코야키`

### 이번에 바꾼 레버

- `batch path에서 auto를 기본값처럼 사용`한 것만 바꿨습니다.
- 별도의 수동 `prepare_mode` override는 주지 않았습니다.

## 4. 무엇을 바꿨는가

1. `scripts/local_video_ltx_auto_full_sample_validation.py`
   - 전체 샘플 11장에 대해 `local_video_ltx_first_try.py --prepare-mode auto`를 실행하는 batch validation 스크립트를 추가했습니다.
   - 각 결과에 대해 `resolved_prepare_mode`, `auto_shot_type`, metric 요약을 남기도록 구성했습니다.

## 5. 결과

artifact:

- `docs/experiments/artifacts/exp-73-local-ltx-auto-full-sample-validation/summary.json`

### aggregate

- completed: `11 / 11`
- average elapsed seconds: `11.78`
- average mid-frame MSE: `357.27`
- average mid-frame edge variance: `863.89`

### prepare_mode 분포

- `cover_center`: `2`
- `contain_blur`: `7`
- `cover_top`: `2`

### shot type 분포

- `tray_full_plate`: `2`
- `preserve_shot`: `7`
- `glass_drink_candidate`: `2`

### 이미지별 핵심 관찰

1. `규카츠`, `타코야키`
   - `tray_full_plate -> cover_center`로 분기됐습니다.
2. `커피`, `맥주`
   - `glass_drink_candidate -> cover_top`으로 분기됐습니다.
3. `라멘`, `순두부짬뽕`, `장어덮밥`, `귤모찌`, `초코소보로호두과자`, `카오위`, `아이스크림`
   - `preserve_shot -> contain_blur`로 분기됐습니다.

### 확인된 것

1. `auto`는 known baseline set 밖의 샘플까지 포함한 전체 11장에서도 일관된 shot type 분기를 만들었습니다.
2. current baseline 정책은 batch path에서도 그대로 유지됩니다.
3. `커피`, `맥주`는 모두 `cover_top`으로 잘 분기됐습니다.

## 6. 실패/제약

1. `타코야키`는 mid-frame MSE가 `1260.01`로 높게 나왔습니다.
   - 다만 시각적으로는 완전 붕괴라기보다 구성 변화와 디테일 손실이 섞인 케이스라, 이 수치 하나만으로 실패로 단정하긴 어렵습니다.
2. `맥주`도 MSE가 높은 편(`797.78`)이라 drink shot은 여전히 prompt/seed 민감도가 남아 있습니다.
3. `카오위`는 영문 라벨을 정확히 특정하기 어려워 generic prompt에 가깝게 넣었습니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - `prepare_mode auto`는 이제 batch validation에서도 기본 후보로 써도 되는 수준입니다.
  - 다만 shot type 분기 안정성과 별개로, 일부 샘플은 여전히 생성 품질 자체가 별도 병목입니다.

## 8. 다음 액션

1. 다음은 batch runner 계열 실험에서 `auto`를 기본값으로 승격하는 것입니다.
2. 그 다음은 `타코야키`, `맥주`처럼 auto 분기는 맞지만 결과가 거친 샘플에 대해 `shot type`별 후속 레버를 따로 보는 편이 맞습니다.

# EXP-236 Shot-aware Renderer Baseline Matrix

## 1. 기본 정보

- 실험 ID: `EXP-236`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `b_grade_fun shot-aware renderer baseline freeze / template-sample matrix`

## 2. 왜 이 작업을 했는가

- `EXP-235`까지로 `T02 / promotion`과 `T04 / review`에서 대표 샘플 4종은 이미 확인했습니다.
- 하지만 그 상태만으로는 현재 baseline을 팀 공용 기준선으로 계속 써도 되는지, 그리고 helper 함수와 실제 본선 정책이 완전히 같은 방향을 보고 있는지까지는 닫히지 않았습니다.
- 특히 `services/worker/renderers/framing.py`의 `choose_prepare_mode()`는 preserve shot에서 아직 `contain_blur`를 반환하고 있었고, 실제 본선 policy는 이미 `cover_center`로 넘어간 상태였습니다.
- 따라서 이번 작업에서는 helper parity를 먼저 맞추고, 그 뒤 `T02/T04 x canonical sample pool` 매트릭스를 한 번에 돌려 baseline을 freeze 가능한지 확인했습니다.

## 3. 실험 질문

1. 현재 `b_grade_fun` shot-aware baseline은 `T02`, `T04` 전체에서 그대로 유지 가능한가
2. `tray / drink / preserve` 세 lane이 canonical sample pool 확장 시에도 일관되게 재현되는가
3. helper-level `choose_prepare_mode()`와 실제 renderer 첫 scene policy가 같은 기준선을 보고 있는가

## 4. 실행 조건

### 4.1 템플릿

- `T02 / promotion / b_grade_fun`
- `T04 / review / b_grade_fun`

### 4.2 샘플군

- tray 계열:
  - `규카츠`
  - `타코야키`
- drink 계열:
  - `맥주`
  - `커피`
- preserve 계열:
  - `라멘`
  - `순두부짬뽕`
  - `장어덮밥`
  - `귤모찌`

### 4.3 실행 방식

- 새 스크립트:
  - `scripts/shot_aware_renderer_baseline_matrix.py`
- artifact root:
  - `docs/experiments/artifacts/exp-236-shot-aware-renderer-baseline-matrix/`

## 5. 핵심 변경

1. `services/worker/renderers/framing.py`
   - `choose_prepare_mode()`의 preserve 기본값을 `contain_blur`에서 `cover_center`로 정렬했습니다.
2. `services/worker/tests/test_generation_pipeline.py`
   - `라멘` preserve shot에 대해 classifier/prepare mode parity 검증을 추가했습니다.
3. `scripts/shot_aware_renderer_baseline_matrix.py`
   - 실제 worker generation pipeline을 돌려 `T02/T04 x 8샘플 = 16 run`을 한 번에 재현하는 baseline matrix runner를 추가했습니다.

## 6. 핵심 결과

### 6.1 template 관점

- `T02`
  - sample `8건`
  - shot type 분포:
    - `tray_full_plate 2`
    - `glass_drink_candidate 2`
    - `preserve_shot 4`
  - first scene classifier parity: `8/8`
  - 평균 `avg_rgb_diff`: `12.3`

- `T04`
  - sample `8건`
  - shot type 분포:
    - `tray_full_plate 2`
    - `glass_drink_candidate 2`
    - `preserve_shot 4`
  - first scene classifier parity: `8/8`
  - 평균 `avg_rgb_diff`: `11.75`

### 6.2 lane 관점

- `tray_full_plate`
  - `T02`: `cover_center -> cover_center -> cover_top -> cover_center`
  - `T04`: `cover_center -> cover_center -> cover_center`
- `glass_drink_candidate`
  - `맥주`: `cover_bottom` anchor 유지
  - `커피`: `cover_top` anchor 유지
  - `T02`의 `period` scene에서만 `cover_center` override가 들어감
- `preserve_shot`
  - `T02`: `cover_center -> cover_center -> cover_top -> cover_center`
  - `T04`: `cover_center -> cover_center -> cover_center`
  - helper parity도 이제 `cover_center`로 일치함

### 6.3 시각 확인

- 대표 contact sheet 기준으로 `규카츠`, `맥주`, `라멘`, `T04 라멘`까지 직접 확인했습니다.
- 이번 매트릭스에서는 과한 crop 회귀나 blur backdrop 재등장, drink anchor 붕괴는 보이지 않았습니다.

## 7. 해석

1. 이번 시점에서 `b_grade_fun` shot-aware baseline은 `대표 4샘플만 우연히 맞는 상태`가 아니라 `canonical sample pool`로 넓혀도 재현되는 상태에 가깝습니다.
2. `preserve lane`은 정책 자체뿐 아니라 helper 함수까지 정렬됐기 때문에, 이후 script/benchmark/본선 코드가 서로 다른 prepare mode를 말하는 혼선도 줄었습니다.
3. 즉 지금은 새 OVAAT를 더 이어서 미세조정할 타이밍보다, 현재 baseline을 기준선으로 간주하고 다음 흐름으로 넘기는 편이 맞습니다.

## 8. 결론

- 판정은 `baseline freeze 가능`입니다.
- 현재 `b_grade_fun` shot-aware renderer baseline은 아래 기준으로 유지합니다.
  - tray: `cover_center`, `T02 period`만 `cover_top`
  - drink: anchor 기반 `cover_top / cover_bottom`, `T02 period`만 `cover_center`
  - preserve: 기본 `cover_center`, `T02 period`만 `cover_top`

## 9. 다음 액션

1. 이 baseline을 더 미세하게 흔들기보다, `결과 확인 UX / template-result package` 흐름에서 이 기준선을 어떻게 보여주고 설명할지로 다시 넘어갑니다.
2. 새 영상 모델 비교 실험은 이 baseline보다 명확히 높은 상한을 보여줄 때만 제한적으로 추가하는 편이 맞습니다.
3. 이후 비교 실험이 필요하면 `EXP-236` sample matrix를 regression gate로 재사용합니다.

## 10. 대표 artifact

- `docs/experiments/artifacts/exp-236-shot-aware-renderer-baseline-matrix/summary.json`
- `docs/experiments/artifacts/exp-236-shot-aware-renderer-baseline-matrix/T02/규카츠/contact_sheet.png`
- `docs/experiments/artifacts/exp-236-shot-aware-renderer-baseline-matrix/T02/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-236-shot-aware-renderer-baseline-matrix/T02/라멘/contact_sheet.png`
- `docs/experiments/artifacts/exp-236-shot-aware-renderer-baseline-matrix/T04/라멘/contact_sheet.png`

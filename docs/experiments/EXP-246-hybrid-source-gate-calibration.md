# EXP-246 Hybrid Source Gate Calibration

## 1. 기본 정보

- 실험 ID: `EXP-246`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `hybrid packaging lane에 태울 generated source clip acceptance gate 고정`

## 2. 왜 이 작업을 했는가

- `EXP-245`까지로 generated mp4를 실제 generation pipeline에 넣는 길은 열렸습니다.
- 하지만 그 다음 질문은 `무슨 clip이든 hybrid lane에 태우면 되는가`가 아니었습니다.
- 지금 필요한 것은 `어떤 generated clip은 태우고`, `어떤 clip은 manual review로 보내고`, `어떤 clip은 아예 버릴지`를 자동으로 가르는 최소 gate입니다.

## 3. 이번에 바꾼 것

### 3.1 gate helper 추가

- `scripts/video_quality_gate.py`
  - benchmark 결과의 `mid_frame_metrics.mse`, `motion_metrics.avg_rgb_diff`, `packaging_fit`, `provider`를 읽어 hybrid source gate를 계산합니다.
  - decision은 아래 4개 중 하나로 고정했습니다.
    - `native_control`
    - `accept`
    - `manual_review`
    - `reject`

### 3.2 benchmark summary 자동 annotation

- `scripts/video_upper_bound_benchmark.py`
  - 이제 benchmark를 새로 돌리면 top-level `summary.json`에 각 provider별 `hybrid_source_gate`와 전체 `hybrid_source_gate_summary`가 자동으로 붙습니다.

### 3.3 calibration report runner 추가

- `scripts/run_hybrid_source_gate_report.py`
  - 기존 benchmark summary를 다시 읽어 gate report를 뽑는 리포터를 추가했습니다.
  - 이번 calibration에서는 `EXP-238`, `EXP-239` artifact를 그대로 재사용했습니다.

### 3.4 테스트 추가

- `services/worker/tests/test_video_quality_gate.py`
  - `accept / manual_review / reject / native_control` 분기와 top-level summary count 집계를 검증했습니다.

## 4. 이번에 고정한 기준

### 4.1 preserve gate

- `pass`: `mid_frame_metrics.mse <= 3000`
- `hold`: `3000 < mse <= 6500`
- `fail`: `mse > 6500`

해석:

- `pass`는 원본 정체성이 충분히 유지된 clip입니다.
- `hold`는 hybrid source로 쓸 가능성은 있지만, 정체성 drift를 사람이 확인해야 하는 clip입니다.
- `fail`은 source 단계에서 이미 identity drift가 크다고 보는 clip입니다.

### 4.2 motion gate

- `fail`: `avg_rgb_diff < 6.5`
- `hold`: `6.5 <= avg_rgb_diff < 10.0`
- `pass`: `avg_rgb_diff >= 10.0`

해석:

- 이 gate는 `광고형 motion이 충분한가`보다 먼저, `정지 포스터 수준인지 아닌지`를 자르기 위한 최소 조건입니다.
- 따라서 `hold`는 약한 움직임이지만 hybrid packaging으로 보완할 여지가 있는 상태를 뜻합니다.

### 4.3 hybrid source decision

- `native_control`
  - 이미 `product_control` 계열이라 hybrid source gate가 아니라 native control lane으로 봅니다.
- `accept`
  - preserve `pass`이고 motion이 `fail`이 아닌 generated clip
- `manual_review`
  - preserve `hold`이고 motion이 `fail`이 아닌 generated clip
- `reject`
  - preserve `fail` 또는 motion `fail`

## 5. calibration 실행

### 5.1 정적 검증

```bash
python -m py_compile scripts/video_quality_gate.py scripts/video_upper_bound_benchmark.py scripts/run_hybrid_source_gate_report.py services/worker/tests/test_video_quality_gate.py
```

### 5.2 테스트

```bash
uv run --project services/worker pytest services/worker/tests/test_video_quality_gate.py -q
```

결과:

- `4 passed`

### 5.3 calibration report 생성

```bash
python scripts/run_hybrid_source_gate_report.py
```

### 5.4 benchmark annotation smoke

```bash
python scripts/video_upper_bound_benchmark.py --benchmark-id EXP-246-benchmark-annotation-smoke --providers product_control_motion --images "docs\sample\음식사진샘플(맥주).jpg" --output-dir docs/experiments/artifacts/exp-246-benchmark-annotation-smoke
```

## 6. calibration 결과

artifact root:

- `docs/experiments/artifacts/exp-246-hybrid-source-gate-calibration/`

aggregate summary:

- `native_control`: `3`
- `accept`: `2`
- `manual_review`: `3`
- `reject`: `1`

provider별:

- `product_control_motion`
  - `native_control = 3`
- `sora2_current_best`
  - `accept = 2`
  - `manual_review = 1`
- `manual_veo`
  - `manual_review = 2`
  - `reject = 1`

## 7. 해석

1. `sora2_current_best / 맥주`는 두 benchmark 모두 `accept`로 떨어졌습니다.
2. 즉 현재 기준으로는 `drink lane`에서는 hybrid source로 태워볼 가치가 있는 clip이 분명히 존재합니다.
3. 반면 `sora2_current_best / 규카츠`는 `manual_review`로 떨어졌습니다.
4. 즉 `tray/full-plate lane`은 아직 자동 acceptance로 올릴 수준이 아니고, 사람이 drift를 한 번 더 봐야 합니다.
5. `manual_veo / 규카츠`는 `reject`가 나왔습니다.
6. 즉 quality upper-bound reference라고 해서 hybrid source 자동 후보가 되는 것은 아니며, preserve gate를 넘지 못하면 그대로 탈락시키는 편이 맞습니다.

## 8. 결론

- 이제 `hybrid lane source selection`은 말로만 하는 판단이 아니라, 현재 저장소에서 반복 실행 가능한 gate로 고정됐습니다.
- 중요한 점은 이 gate가 `본선 승격 판정`이 아니라 `hybrid packaging에 태워볼 가치가 있는 source인지`를 먼저 거르는 1차 필터라는 것입니다.
- 현재까지의 calibration 기준으로는:
  - `맥주 / sora2_current_best`: `accept`
  - `규카츠 / sora2_current_best`: `manual_review`
  - `규카츠 / manual_veo`: `reject`

## 9. 다음 액션

1. hybrid lane 입력을 받을 때 이 gate를 직접 호출하는 `candidate selection` 스크립트를 추가합니다.
2. `manual_review`로 떨어진 tray lane clip은 contact sheet review를 거쳐 승인/반려 사례를 더 쌓습니다.
3. 기준이 더 쌓이면 `preserve pass/hold` 임계값을 tray lane과 drink lane으로 분리할지 검토합니다.

## 10. 대표 artifact

- `docs/experiments/artifacts/exp-246-hybrid-source-gate-calibration/report.json`
- `docs/experiments/artifacts/exp-246-benchmark-annotation-smoke/summary.json`

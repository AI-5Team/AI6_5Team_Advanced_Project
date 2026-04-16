# EXP-247 Hybrid Source Selection Flow Spike

## 1. 기본 정보

- 실험 ID: `EXP-247`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `hybrid source gate 결과를 실제 generation pipeline 입력 선택 흐름에 연결`

## 2. 왜 이 작업을 했는가

- `EXP-246`까지로 gate 기준은 생겼지만, 실제로는 여전히 사람이 직접 `hybridSourceVideoPath`를 써 넣어야 했습니다.
- 즉 `accept / manual_review / reject`가 문서상 판정으로만 남아 있었고, 실제 generation spike 실행 경로에는 아직 연결되지 않았습니다.
- 이번 작업의 목적은 gate를 말로만 쓰는 것이 아니라, `accept면 자동 선택`, `manual_review면 기본 차단`, `필요할 때만 명시적으로 허용`하는 실제 입력 선택 흐름으로 연결하는 것입니다.

## 3. 이번에 바꾼 것

### 3.1 source selection helper 추가

- `scripts/hybrid_source_selection.py`
  - benchmark `summary.json`을 읽고 provider별 `hybrid_source_gate`를 기반으로 candidate를 수집합니다.
  - 기본 규칙은 아래와 같습니다.
    - `accept`만 자동 선택
    - `manual_review`는 `--allow-manual-review`가 있을 때만 선택 가능
    - `product_control_*`는 hybrid source 자동 선택 대상에서 제외
  - 선택 결과는 `build_hybrid_source_selection_snapshot()`으로 provenance snapshot을 만듭니다.

### 3.2 hybrid spike runner 확장

- `scripts/run_hybrid_generation_pipeline_spike.py`
  - 이제 두 가지 모드를 지원합니다.
    - manual mode: 기존처럼 sample image + source video를 직접 지정
    - benchmark_gate mode: benchmark summary에서 `label/provider` 조건으로 source를 자동 선택
  - benchmark gate mode에서는 선택 provenance를 `hybridSourceSelection`으로 `input_snapshot_json`에 함께 넣습니다.

### 3.3 render meta provenance 기록

- `services/worker/pipelines/generation.py`
  - `input_snapshot.hybridSourceSelection`을 읽어 `rendererHybridSourceSelection`으로 `render-meta.json`에 남기도록 확장했습니다.
  - 즉 결과물만 보고도 `어느 benchmark`, `어느 provider`, `어느 gate decision`에서 왔는지 추적할 수 있습니다.

### 3.4 테스트 추가

- `services/worker/tests/test_hybrid_source_selection.py`
  - `accept` 우선 선택
  - `manual_review` 기본 차단
  - `--allow-manual-review` 허용 시 선택 가능
  - selection snapshot 생성
- `services/worker/tests/test_generation_pipeline.py`
  - hybrid selection provenance가 `render-meta.json`까지 전파되는지 검증을 추가했습니다.

## 4. 실행 및 검증

### 4.1 정적 검증

```bash
python -m py_compile scripts/hybrid_source_selection.py scripts/run_hybrid_generation_pipeline_spike.py services/worker/pipelines/generation.py services/worker/tests/test_generation_pipeline.py services/worker/tests/test_hybrid_source_selection.py
```

### 4.2 테스트

```bash
uv run --project services/worker pytest services/worker/tests/test_media_renderer.py services/worker/tests/test_generation_pipeline.py services/worker/tests/test_video_quality_gate.py services/worker/tests/test_hybrid_source_selection.py -q
```

결과:

- `33 passed`

### 4.3 accepted candidate 자동 선택 spike

```bash
python scripts/run_hybrid_generation_pipeline_spike.py --experiment-id EXP-247-hybrid-source-selection-flow-spike --output-dir docs/experiments/artifacts/exp-247-hybrid-source-selection-flow-spike --benchmark-summary docs/experiments/artifacts/exp-239-sora2-current-best-vs-control-two-sample-check/summary.json --label 맥주
```

### 4.4 manual review 기본 차단 smoke

```bash
python scripts/run_hybrid_generation_pipeline_spike.py --experiment-id EXP-247-manual-review-block-smoke --output-dir docs/experiments/artifacts/exp-247-manual-review-block-smoke --benchmark-summary docs/experiments/artifacts/exp-239-sora2-current-best-vs-control-two-sample-check/summary.json --label 규카츠
```

결과:

- `ValueError: no accepted hybrid source candidate found ... available decisions=['manual_review', 'reject']`

## 5. 결과

artifact root:

- `docs/experiments/artifacts/exp-247-hybrid-source-selection-flow-spike/`

자동 선택 결과:

- benchmark: `EXP-239-sora2-current-best-vs-control-two-sample-check`
- label: `맥주`
- provider: `sora2_current_best`
- gate decision: `accept`
- source video: `exp-239 ... / sora2_current_best / 맥주 / run / 맥주 / sora2_first_try.mp4`

최종 hybrid output:

- `rendererVideoSourceMode=hybrid_generated_clip`
- `rendererMotionMode=hybrid_overlay_packaging`
- `rendererHybridDurationStrategy=freeze_last_frame`
- `finalVideoDurationSec=6.3`

또한 summary와 render meta 모두에 아래 provenance가 같이 남았습니다.

- `benchmarkId`
- `label`
- `provider`
- `gateDecision`
- `gateReason`
- `midFrameMse`
- `motionAvgRgbDiff`

## 6. 해석

1. 이제 hybrid lane은 `source clip을 사람이 수동으로 꽂는 실험용 경로`에서 한 단계 더 나아갔습니다.
2. `accept`가 나온 clip은 실제 generation spike에 자동으로 태울 수 있고, provenance도 결과물에 남습니다.
3. 반대로 `manual_review`나 `reject`는 기본적으로 막히기 때문에, tray lane처럼 보존 drift가 남아 있는 케이스를 실수로 자동 승격시키지 않게 됐습니다.
4. 특히 `규카츠`가 기본 차단된 점은, 지금 tray/full-plate lane을 drink lane과 같은 자동화 수준으로 취급하면 안 된다는 것을 다시 확인해 줍니다.

## 7. 결론

- `EXP-246`의 gate는 이번 작업으로 실제 실행 경로에 연결됐습니다.
- 지금 기준으로 hybrid lane 자동 선택은 `accept` candidate까지만 허용하는 편이 맞고, `manual_review`는 명시적 opt-in이 필요합니다.
- 따라서 다음 단계는 `manual_review queue`를 별도 문서/스크립트로 두거나, 아예 API/worker 입력 단계에서 이 분기를 공통 처리하는 것입니다.

## 8. 다음 액션

1. `manual_review` candidate를 별도 queue artifact로 내보내는 helper를 추가합니다.
2. benchmark gate 기반 selection snapshot을 API request 작성 경로에도 연결할지 검토합니다.
3. tray/full-plate lane은 review case 누적 후 `manual_review -> accept` 승격 조건을 별도로 정리합니다.

## 9. 대표 artifact

- `docs/experiments/artifacts/exp-247-hybrid-source-selection-flow-spike/summary.json`
- `docs/experiments/artifacts/exp-247-hybrid-source-selection-flow-spike/hybrid_selection_contact_sheet_7up.png`

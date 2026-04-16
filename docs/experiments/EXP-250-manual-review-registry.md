# EXP-250 Manual Review Registry

## 1. 기본 정보

- 실험 ID: `EXP-250`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `manual_review decision log를 selection 경로에 다시 연결하는 승인 레지스트리`

## 2. 왜 이 작업을 했는가

- `EXP-249`까지로 사람의 판단은 남길 수 있게 됐지만, 그 판단이 다시 selection 경로에 반영되지는 않았습니다.
- 즉 `manual_review -> promote`가 되어도 generation spike는 여전히 이를 모른 채 `accept`만 찾게 됩니다.
- 이번 작업의 목적은 `decision log`를 읽는 승인 레지스트리를 만들고, `promote`된 후보만 selection 경로에 다시 진입시키는 것입니다.

## 3. 이번에 바꾼 것

### 3.1 approval registry helper 추가

- `scripts/manual_review_registry.py`
  - decision artifact 디렉터리를 읽어 `decision.json`들을 수집합니다.
  - `hold / promote / reject` 집계를 만들고, `promote`된 candidate key만 별도로 로드할 수 있게 했습니다.

### 3.2 selection helper 확장

- `scripts/hybrid_source_selection.py`
  - 이제 candidate마다 `candidateKey`를 가집니다.
  - `manual_review_decisions_dir`를 넘기면 `promote`된 manual-review 후보를 읽어 selection 후보에 다시 포함합니다.
  - snapshot에는 아래 provenance가 추가됩니다.
    - `candidateKey`
    - `reviewFinalDecision`
    - `reviewDecisionPath`
    - `reviewer`
    - `reviewDecidedAt`
  - 이 경우 `selectionMode=promoted_manual_review`로 남깁니다.

### 3.3 spike runner 확장

- `scripts/run_hybrid_generation_pipeline_spike.py`
  - `--manual-review-decisions-dir` 인자를 추가했습니다.
  - 이 경로를 주면 selection helper가 승인된 manual-review 후보를 읽을 수 있습니다.

### 3.4 테스트 추가

- `services/worker/tests/test_manual_review_registry.py`
  - registry 집계와 promote lookup 검증
- `services/worker/tests/test_hybrid_source_selection.py`
  - `promote`된 manual-review 후보는 선택 가능
  - `hold` 상태는 registry가 있어도 계속 차단

## 4. 실행 및 검증

### 4.1 정적 검증

```bash
python -m py_compile scripts/manual_review_registry.py scripts/run_manual_review_registry_report.py scripts/hybrid_source_selection.py scripts/run_hybrid_generation_pipeline_spike.py services/worker/tests/test_hybrid_source_selection.py services/worker/tests/test_manual_review_registry.py
```

### 4.2 테스트

```bash
uv run --project services/worker pytest services/worker/tests/test_manual_review_registry.py services/worker/tests/test_manual_review_decision.py services/worker/tests/test_manual_review_queue.py services/worker/tests/test_hybrid_source_selection.py services/worker/tests/test_video_quality_gate.py -q
```

결과:

- `18 passed`

### 4.3 registry report 생성

```bash
python scripts/run_manual_review_registry_report.py
```

### 4.4 hold candidate block smoke

```bash
python scripts/run_hybrid_generation_pipeline_spike.py --experiment-id EXP-250-hold-registry-block-smoke --output-dir docs/experiments/artifacts/exp-250-hold-registry-block-smoke --benchmark-summary docs/experiments/artifacts/exp-239-sora2-current-best-vs-control-two-sample-check/summary.json --label 규카츠 --manual-review-decisions-dir docs/experiments/artifacts/exp-249-manual-review-decision-log
```

결과:

- `ValueError: no accepted hybrid source candidate found ... available decisions=['manual_review', 'reject']`

## 5. 결과

registry artifact:

- `docs/experiments/artifacts/exp-250-manual-review-registry/report.json`

현재 registry 상태:

- entryCount: `1`
- decisionCounts: `{"hold": 1}`
- promotedCandidateKeys: `[]`

의미:

- 현재 decision log 기준으로 승인된 manual-review 후보는 없습니다.
- 즉 `규카츠 / sora2_current_best`는 아직 selection 경로로 복귀하지 않습니다.

## 6. 해석

1. 이제 selection 경로는 `accept`뿐 아니라, 명시적으로 `promote`된 manual-review 후보도 다시 받을 수 있습니다.
2. 반대로 `hold` 상태는 registry가 있어도 계속 차단되므로, 예비 판단 후보가 실수로 본선 경로에 섞이지 않습니다.
3. 현재 기준으로는 `promote=0`이므로, hybrid lane 자동 선택은 여전히 drink 쪽 accepted candidate에만 한정됩니다.

## 7. 결론

- `manual_review -> decision log -> approval registry -> selection` 경로가 코드상으로 연결됐습니다.
- 다만 실제 registry에는 아직 `promote`가 없으므로, 운영상 다음 액션은 `규카츠` 후보를 실제 video 재생 기준으로 재판정하는 것입니다.

## 8. 다음 액션

1. `규카츠` source clip을 실제 재생 기준으로 다시 보고 `hold -> promote/reject`를 확정합니다.
2. `promote`가 나오면 registry를 그대로 사용해 hybrid generation spike를 재실행합니다.
3. 이후 API/worker 입력 경로에도 같은 registry 분기를 공통 적용합니다.

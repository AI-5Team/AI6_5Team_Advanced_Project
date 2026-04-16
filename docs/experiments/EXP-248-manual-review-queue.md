# EXP-248 Manual Review Queue

## 1. 기본 정보

- 실험 ID: `EXP-248`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `hybrid source gate의 manual_review 후보를 사람이 확인할 queue artifact로 분리`

## 2. 왜 이 작업을 했는가

- `EXP-247`까지로 `accept` 후보는 자동 선택되고 `manual_review`는 기본 차단되도록 연결됐습니다.
- 다만 차단만 해서는 다음 액션이 없습니다. 어떤 후보를 사람이 봐야 하는지 따로 뽑히지 않으면, tray/full-plate lane은 계속 "막혀 있는 상태"로만 남습니다.
- 이번 작업의 목적은 `manual_review`를 단순한 실패가 아니라, `검토 대기 상태`로 다룰 수 있게 queue artifact를 만드는 것입니다.

## 3. 이번에 바꾼 것

### 3.1 manual review helper 추가

- `scripts/manual_review_queue.py`
  - benchmark summary에서 `manual_review` 후보만 추출합니다.
  - 기본값으로는 `role=hybrid_source_candidate`만 queue에 넣고, `reference_only`는 제외합니다.
  - 각 항목에 `reviewCategory`, `recommendedAction`, 입력/비디오/contact sheet/summary 경로를 같이 남깁니다.

### 3.2 queue report runner 추가

- `scripts/run_manual_review_queue_report.py`
  - 기본적으로 `EXP-238`, `EXP-239` summary를 읽어 queue artifact를 생성합니다.
  - 산출물은 아래 두 가지입니다.
    - `report.json`
    - `queue.md`
  - 선택적으로 `--label`, `--provider`, `--include-reference-only` 필터를 줄 수 있습니다.

### 3.3 테스트 추가

- `services/worker/tests/test_manual_review_queue.py`
  - `reference_only` 기본 제외
  - `include_reference_only=True`일 때 포함
  - report/markdown 생성 검증

## 4. 실행 및 검증

### 4.1 정적 검증

```bash
python -m py_compile scripts/manual_review_queue.py scripts/run_manual_review_queue_report.py services/worker/tests/test_manual_review_queue.py
```

### 4.2 테스트

```bash
uv run --project services/worker pytest services/worker/tests/test_manual_review_queue.py services/worker/tests/test_hybrid_source_selection.py services/worker/tests/test_video_quality_gate.py -q
```

결과:

- `11 passed`

### 4.3 queue artifact 생성

```bash
python scripts/run_manual_review_queue_report.py
```

## 5. 결과

artifact root:

- `docs/experiments/artifacts/exp-248-manual-review-queue/`

기본 queue 결과:

- total entries: `1`
- review category counts: `{"promotion_candidate": 1}`

남은 후보:

- benchmark: `EXP-239-sora2-current-best-vs-control-two-sample-check`
- label: `규카츠`
- provider: `sora2_current_best`
- decision: `manual_review`
- role: `hybrid_source_candidate`
- recommended action: `identity_review_then_promote_if_pass`
- midFrameMse: `3545.57`
- motionAvgRgbDiff: `21.04`

제외된 것:

- `manual_veo` 계열은 기본값으로 queue에 넣지 않았습니다.
- 이유는 `manual_review`여도 `role=reference_only`라서, 본선 승격 후보가 아니라 비교 기준선에 가깝기 때문입니다.

## 6. 해석

1. 지금 기준에서 사람이 실제로 봐야 할 hybrid 승격 후보는 많지 않습니다. 기본 queue 기준으로는 `규카츠 / sora2_current_best` 한 건만 남습니다.
2. 즉 문제는 "manual review가 너무 많다"가 아니라, tray/full-plate lane에서 승격 판단을 내려야 하는 소수 후보가 아직 닫히지 않았다는 쪽에 가깝습니다.
3. 이 queue가 생기면서 앞으로는 `accept는 자동`, `manual_review는 queue`, `reject/reference_only는 연구 참고`라는 세 갈래 운영이 가능합니다.

## 7. 결론

- `manual_review`는 더 이상 막연한 상태값이 아니라, 실제 검토 대상 목록으로 분리됐습니다.
- 지금 다음 실험은 새 모델을 무한히 붙이는 것보다, 이 queue에 올라온 candidate를 어떤 기준으로 `accept`로 승격할지 정하는 쪽이 더 맞습니다.

## 8. 다음 액션

1. `queue.md`를 기준으로 `규카츠` candidate의 보존 실패 포인트를 사람이 판정할 checklist를 정리합니다.
2. review 결과를 다시 `accept / reject`로 기록하는 승격 로그 포맷을 정합니다.
3. 필요하면 이후 API/worker 입력 경로에도 같은 queue 분기를 공통 적용합니다.

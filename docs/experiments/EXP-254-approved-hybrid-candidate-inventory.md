# EXP-254 Approved Hybrid Candidate Inventory

## 1. 기본 정보

- 실험 ID: `EXP-254`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `accept + promoted manual_review 후보를 lane별 approved inventory로 통합`

## 2. 왜 이 작업을 했는가

- `EXP-253`까지로 approved candidate를 API generate 경로에 태울 수는 있게 됐지만, 지금 기준으로 어떤 후보가 실제 approved baseline인지 한눈에 보는 inventory는 없었습니다.
- 이 상태에서는 다음 실험이 기존 승인 후보를 재사용하는지, 아니면 다시 임시 판단으로 돌아가는지 기준이 흐려집니다.
- 이번 작업의 목적은 `benchmark accept`와 `manual_review promote`를 한 리포트로 합쳐, 현재 본선에 올릴 수 있는 hybrid source 후보를 lane별로 고정하는 것입니다.

## 3. 이번에 추가한 것

### 3.1 inventory helper

- `scripts/approved_hybrid_inventory.py`
  - benchmark summary에서 `accept`된 hybrid source candidate를 수집합니다.
  - manual review decision log에서 `promote`된 candidate를 함께 읽어 approved inventory에 합칩니다.
  - label 기준으로 `serviceLane`을 부여합니다.
    - `맥주 -> drink_glass_lane`
    - `규카츠 -> tray_full_plate_lane`
  - `recommendedByLane`, `recommendedByLabel`도 같이 계산합니다.

### 3.2 inventory report runner

- `scripts/run_approved_hybrid_inventory_report.py`
  - 기본값으로 `EXP-238`, `EXP-239` benchmark summary와 `EXP-249` decision log를 읽습니다.
  - artifact를 아래 위치에 생성합니다.
    - `docs/experiments/artifacts/exp-254-approved-hybrid-candidate-inventory/report.json`
    - `docs/experiments/artifacts/exp-254-approved-hybrid-candidate-inventory/inventory.md`

### 3.3 테스트

- `services/worker/tests/test_approved_hybrid_inventory.py`
  - `benchmark_accept`와 `manual_review_promote`가 하나의 approved inventory로 합쳐지는지 검증합니다.

## 4. 실행 및 검증

### 4.1 정적 검증

```bash
python -m py_compile scripts/approved_hybrid_inventory.py scripts/run_approved_hybrid_inventory_report.py services/worker/tests/test_approved_hybrid_inventory.py
```

### 4.2 테스트

```bash
uv run --project services/worker pytest services/worker/tests/test_approved_hybrid_inventory.py services/worker/tests/test_manual_review_registry.py services/worker/tests/test_hybrid_source_selection.py -q
```

결과:

- `8 passed`

### 4.3 실제 inventory artifact 생성

```bash
python scripts/run_approved_hybrid_inventory_report.py
```

## 5. 결과

artifact summary:

- `docs/experiments/artifacts/exp-254-approved-hybrid-candidate-inventory/report.json`
- `docs/experiments/artifacts/exp-254-approved-hybrid-candidate-inventory/inventory.md`

현재 inventory 상태:

- `itemCount=3`
- `laneCounts={"drink_glass_lane": 2, "tray_full_plate_lane": 1}`
- `approvalSourceCounts={"benchmark_accept": 2, "manual_review_promote": 1}`

lane별 추천 후보:

1. `drink_glass_lane`
   - `EXP-238-sora2-lane-reopen-beer-check::맥주::sora2_current_best`
   - `approvalSource=benchmark_accept`
   - `midFrameMse=2898.03`
   - `motionAvgRgbDiff=7.91`
2. `tray_full_plate_lane`
   - `EXP-239-sora2-current-best-vs-control-two-sample-check::규카츠::sora2_current_best`
   - `approvalSource=manual_review_promote`
   - `midFrameMse=3545.57`
   - `motionAvgRgbDiff=21.04`

## 6. 해석

1. 이제 drink lane은 `benchmark accept`만으로도 approved inventory가 2건 존재합니다.
2. tray/full-plate lane은 아직 `manual_review -> promote`로 닫힌 후보 1건뿐입니다.
3. 즉 현재 기준으로 `drink lane은 gate 기반`, `tray lane은 review 기반`이라는 운영 차이가 명확해졌습니다.
4. 앞으로 새 실험은 이 inventory에 후보를 추가하는 방향으로 관리하는 편이 맞고, 이미 approved된 후보를 다시 임시 판단으로 다루면 안 됩니다.

## 7. 결론

- `approved hybrid candidate inventory`가 생기면서 지금 본선에서 재사용 가능한 후보 집합이 명시적으로 고정됐습니다.
- 따라서 다음 baseline 작업은 `무작정 새 생성`보다 `어느 lane에 approved 후보가 부족한지`를 기준으로 우선순위를 잡을 수 있게 됐습니다.

## 8. 다음 액션

1. web 또는 API generate 진입점에서 label/lane 기준 추천 candidate를 붙일지 판단합니다.
2. tray/full-plate lane은 approved 후보가 1건뿐이므로, 같은 절차로 1~2건 더 확보해야 합니다.
3. drink lane도 `accept` 후보 2건 중 어떤 것을 기본 baseline으로 고정할지 운영 기준을 한 번 더 명시합니다.

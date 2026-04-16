# EXP-255 Approved Hybrid Inventory API Read Path

## 1. 기본 정보

- 실험 ID: `EXP-255`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `approved hybrid candidate inventory를 API에서 바로 조회`

## 2. 왜 이 작업을 했는가

- `EXP-254`로 approved inventory를 만들었더라도, 서비스 쪽에서 이 기준선을 읽을 수 없으면 여전히 문서 전용 artifact에 머뭅니다.
- 이번 작업의 목적은 inventory를 더 키우는 것이 아니라, 현재 기준선을 API에서 그대로 소비할 수 있는 최소 읽기 경로를 붙이는 것입니다.

## 3. 이번에 바꾼 것

1. `services/api/app/core/config.py`
   - `APP_APPROVED_HYBRID_INVENTORY_REPORT_PATH` 설정을 추가했습니다.
2. `services/api/app/services/runtime.py`
   - approved inventory report artifact를 읽어 API 응답 형태로 필터링하는 helper를 추가했습니다.
   - `label`, `serviceLane` 기준 필터를 지원합니다.
3. `services/api/app/api/routes.py`
   - `GET /api/hybrid-candidates/approved`
   - query:
     - `label`
     - `serviceLane`
4. `services/api/tests/test_api_smoke.py`
   - inventory report artifact를 읽는 스모크 테스트를 추가했습니다.

## 4. 실행 및 검증

### 4.1 코드 검증

```bash
python -m py_compile services/api/app/core/config.py services/api/app/schemas/api.py services/api/app/api/routes.py services/api/app/services/runtime.py services/api/tests/test_api_smoke.py
```

### 4.2 테스트

```bash
uv run --project services/worker pytest services/api/tests/test_api_smoke.py -q
```

결과:

- `7 passed`

### 4.3 artifact 생성

- artifact root: `docs/experiments/artifacts/exp-255-approved-hybrid-inventory-api-read-path`
- 생성 파일:
  - `approved_inventory_full.json`
  - `approved_inventory_tray.json`
  - `approved_inventory_beer.json`
  - `summary.json`

## 5. 결과

artifact summary:

- `full.itemCount=3`
- `full.laneCounts={"drink_glass_lane": 2, "tray_full_plate_lane": 1}`
- `full.approvalSourceCounts={"benchmark_accept": 2, "manual_review_promote": 1}`
- `full.recommendedByLane.drink_glass_lane=EXP-238-sora2-lane-reopen-beer-check::맥주::sora2_current_best`
- `full.recommendedByLane.tray_full_plate_lane=EXP-239-sora2-current-best-vs-control-two-sample-check::규카츠::sora2_current_best`
- `trayOnly.itemCount=1`
- `beerOnly.itemCount=2`

## 6. 해석

1. 이제 approved inventory는 문서 artifact에만 남는 것이 아니라, API에서 바로 읽을 수 있는 상태가 됐습니다.
2. 즉 이후 web이나 운영 툴은 같은 기준선을 그대로 조회해서 candidate 추천이나 선택 UI를 붙일 수 있습니다.
3. 이번 단계는 “새 판단 로직 추가”가 아니라, 이미 정리된 inventory를 서비스가 소비할 수 있게 만든 최소 연결입니다.

## 7. 결론

- 지금 단계에서 더 필요한 것은 inventory 계산 레이어를 늘리는 것이 아니라, 이 API를 실제 generate 진입점이나 운영 화면에서 한 번 쓰게 만드는 것입니다.
- 따라서 다음 우선순위는 `추천 candidate 노출` 또는 `tray lane approved 후보 추가 확보` 중 하나입니다.

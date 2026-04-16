# EXP-249 Manual Review Decision Log

## 1. 기본 정보

- 실험 ID: `EXP-249`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `manual_review queue 후보를 review packet과 decision log로 기록`

## 2. 왜 이 작업을 했는가

- `EXP-248`까지로 `manual_review` 후보를 queue artifact로 분리했지만, 아직 실제 판단을 어떻게 남길지는 비어 있었습니다.
- queue만 있으면 "누가 봤는지", "어떤 항목이 hold인지", "최종적으로 promote/reject/hold 중 무엇으로 결정했는지"가 기록되지 않습니다.
- 이번 작업의 목적은 `manual_review`를 실제 운영 행위로 바꾸기 위해 `review packet + decision log` 포맷을 추가하는 것입니다.

## 3. 이번에 바꾼 것

### 3.1 review packet / decision helper 추가

- `scripts/manual_review_decision.py`
  - queue entry를 review packet으로 바꿉니다.
  - checklist는 아래 5개 항목으로 고정했습니다.
    - `main_subject_identity`
    - `peripheral_layout`
    - `text_qr_intrusion`
    - `motion_packaging_fit`
    - `promotion_readiness`
  - 각 항목은 `pending / pass / hold / fail` 상태를 가질 수 있고, 최종 결정은 `hold / promote / reject`로 남깁니다.

### 3.2 decision log runner 추가

- `scripts/run_manual_review_decision_log.py`
  - `EXP-248` queue report를 읽어 review packet을 만들고, candidate별 decision artifact를 생성합니다.
  - 산출물은 아래 세 가지입니다.
    - `review_packet.json`
    - `decision.json`
    - `decision.md`
  - queue가 한 건이면 `candidate-key` 없이도 바로 기록할 수 있게 했습니다.

### 3.3 테스트 추가

- `services/worker/tests/test_manual_review_decision.py`
  - packet 생성
  - candidate key 수집
  - checklist status 반영
  - markdown render

## 4. 실행 및 검증

### 4.1 정적 검증

```bash
python -m py_compile scripts/manual_review_decision.py scripts/run_manual_review_decision_log.py services/worker/tests/test_manual_review_decision.py
```

### 4.2 테스트

```bash
uv run --project services/worker pytest services/worker/tests/test_manual_review_decision.py services/worker/tests/test_manual_review_queue.py services/worker/tests/test_hybrid_source_selection.py services/worker/tests/test_video_quality_gate.py -q
```

결과:

- `15 passed`

### 4.3 예비 decision artifact 생성

```bash
python scripts/run_manual_review_decision_log.py --summary-note "contact sheet 기준으로 메인 규카츠는 유지되지만 프레이밍이 더 타이트해져 주변 구성 보존은 추가 확인이 필요합니다." --check main_subject_identity=pass --check peripheral_layout=hold --check text_qr_intrusion=pass --check motion_packaging_fit=pass --check promotion_readiness=hold --check-note "peripheral_layout=프레이밍이 타이트해 원본의 주변 구성 일부가 잘립니다" --check-note "promotion_readiness=contact sheet 기준 예비판정이며 실제 video 확인이 추가로 필요합니다"
```

## 5. 결과

artifact root:

- `docs/experiments/artifacts/exp-249-manual-review-decision-log/`

생성된 예비 판단:

- candidate: `EXP-239 / 규카츠 / sora2_current_best`
- final decision: `hold`
- reviewer: `codex`
- summary note:
  - `contact sheet 기준으로 메인 규카츠는 유지되지만 프레이밍이 더 타이트해져 주변 구성 보존은 추가 확인이 필요합니다.`

checklist 결과:

- `main_subject_identity=pass`
- `peripheral_layout=hold`
- `text_qr_intrusion=pass`
- `motion_packaging_fit=pass`
- `promotion_readiness=hold`

status counts:

- `pass=3`
- `hold=2`

## 6. 해석

1. 이 후보는 `메인 규카츠 자체`는 비교적 잘 보존됐지만, 프레이밍이 더 타이트해져 주변 구성 보존이 애매합니다.
2. 즉 지금 상태에서는 `reject`까지는 아니지만, 곧바로 `accept`로 승격하기도 이릅니다.
3. 따라서 현재 가장 맞는 운영 상태는 `hold`이며, 다음 판단은 contact sheet가 아니라 실제 clip 재생 확인까지 포함해야 합니다.

## 7. 결론

- 이제 `manual_review`는 queue에서 끝나지 않고, 사람이 어떤 항목을 보고 어떤 결론을 냈는지 decision log까지 남길 수 있게 됐습니다.
- 현재 유일한 승격 검토 후보인 `규카츠 / sora2_current_best`는 contact sheet 기준 예비 판단으로는 `hold`가 맞습니다.

## 8. 다음 액션

1. 실제 video 재생 기준으로 `peripheral_layout`, `promotion_readiness`를 다시 확인합니다.
2. 필요하면 `accept` 승격 조건을 lane별로 더 세분화합니다. 예를 들어 drink lane과 tray lane의 허용 범위를 분리합니다.
3. 이후 API/worker 입력 경로에는 `approved candidate only`를 넣도록 연결합니다.

# EXP-252 Promoted Manual Review Selection Smoke

## 1. 기본 정보

- 실험 ID: `EXP-252`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `promote된 manual-review 후보가 실제 selection 경로에 재진입하는지 검증`

## 2. 왜 이 작업을 했는가

- `EXP-251`에서 `규카츠 / sora2_current_best`를 `promote`로 판단했더라도, 실제 selection helper가 이 결정을 읽지 못하면 운영상 의미가 없습니다.
- 이번 작업의 목적은 decision log -> registry -> hybrid selection 흐름이 실제로 연결되는지 smoke로 확인하는 것입니다.

## 3. 실행

### 3.1 decision promote 반영

```bash
python scripts/run_manual_review_decision_log.py --final-decision promote --summary-note "final hybrid packaging check 기준으로 메인 규카츠와 주요 그릇 구성이 유지되고 text/QR intrusion이 없어 packaging tolerance 안에서 승격 가능합니다." --check main_subject_identity=pass --check peripheral_layout=pass --check text_qr_intrusion=pass --check motion_packaging_fit=pass --check promotion_readiness=pass --check-note "peripheral_layout=원본보다 타이트한 crop이지만 주요 그릇과 소스 구성이 유지되어 packaging tolerance 안으로 판단했습니다" --check-note "promotion_readiness=final hybrid contact sheet 기준 광고 읽힘이 충분해 accept lane 승격 가능으로 판단했습니다"
```

### 3.2 registry 재생성

```bash
python scripts/run_manual_review_registry_report.py
```

### 3.3 selection smoke

```bash
python scripts/run_hybrid_generation_pipeline_spike.py --experiment-id EXP-252-promoted-manual-review-selection-smoke --output-dir docs/experiments/artifacts/exp-252-promoted-manual-review-selection-smoke --benchmark-summary docs/experiments/artifacts/exp-239-sora2-current-best-vs-control-two-sample-check/summary.json --label 규카츠 --manual-review-decisions-dir docs/experiments/artifacts/exp-249-manual-review-decision-log
```

## 4. 결과

decision log:

- `finalDecision=promote`
- `statusCounts={pass: 5}`

registry 상태:

- `entryCount=1`
- `decisionCounts={"promote": 1}`
- `promotedCandidateKeys=["EXP-239-sora2-current-best-vs-control-two-sample-check::규카츠::sora2_current_best"]`

selection smoke 결과:

- `status=completed`
- `hybridSourceSelection.selectionMode=promoted_manual_review`
- `hybridSourceSelection.reviewFinalDecision=promote`
- `rendererHybridSourceSelection.selectionMode=promoted_manual_review`
- `finalVideoDurationSec=6.3`

## 5. 해석

1. 이제 `manual_review` 후보가 단지 문서상 승격되는 것이 아니라, 실제 spike 실행 경로에서 다시 선택될 수 있습니다.
2. selection snapshot과 render meta 모두에 `reviewDecisionPath`, `reviewer`, `reviewDecidedAt`가 남기 때문에 provenance도 유지됩니다.
3. 즉 `accept 자동 선택`과 `promoted manual-review 선택`이 한 경로에서 공존할 수 있게 됐습니다.

## 6. 결론

- `규카츠 / sora2_current_best`는 이제 본선 후보 레지스트리에 들어간 approved candidate로 볼 수 있습니다.
- 다만 이것은 `tray/full-plate lane 전체 승격`이 아니라, `이 특정 candidate의 승인`입니다.

## 7. 다음 액션

1. API/worker 입력 경로에도 같은 registry 분기를 공통 적용합니다.
2. 이후 새 tray/full-plate 후보도 같은 방식으로 `review packet -> decision -> registry`를 거치게 합니다.

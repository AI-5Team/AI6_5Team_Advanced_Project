# EXP-237 Real Video Lane Reopen Beer Check

## 1. 기본 정보

- 실험 ID: `EXP-237`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `실제 영상 생성 lane 재개 가능 여부 / beer single-sample live benchmark`

## 2. 왜 이 작업을 했는가

- 직전 기준선은 `EXP-236`까지로 `shot-aware renderer baseline`을 freeze 가능한 수준으로 정리한 상태였습니다.
- 하지만 이 baseline은 어디까지나 `deterministic motion poster`에 가까운 control입니다.
- 사용자가 지적한 핵심 문제는 맞습니다. 이 상태만으로는 `실제 영상 생성 본선`이라고 보기 어렵습니다.
- 따라서 이번 작업의 목적은 renderer를 더 미세조정하는 것이 아니라, `real video candidate lane`이 지금 실제로 다시 열릴 수 있는지 operational 상태부터 확인하는 것이었습니다.

## 3. 실험 질문

1. 현재 저장소 기준에서 live provider를 이용한 실제 영상 생성 실험을 바로 재개할 수 있는가
2. `product_control_motion`은 실제 영상 생성 후보와 비교할 때 어느 정도 motion 기준선이 되는가
3. 지금 당장 더 해야 할 일은 prompt 미세조정인가, 아니면 provider access 복구인가

## 4. 실행 조건

### 4.1 샘플

- `맥주`

선정 이유:

- 기존 실험에서 가장 품질 reference가 좋았던 샘플입니다.
- drink lane 기준선도 이미 비교적 안정화돼 있어, provider 상태 확인용 single-sample로 적합합니다.

### 4.2 비교군

- `product_control_motion`
- `veo31`
- `sora2_current_best`
- `manual_veo`

### 4.3 실행 커맨드

```bash
python scripts/video_upper_bound_benchmark.py --benchmark-id EXP-237-real-video-lane-reopen-beer-check --providers product_control_motion veo31 sora2_current_best manual_veo --images "docs\sample\음식사진샘플(맥주).jpg" --output-dir docs/experiments/artifacts/exp-237-real-video-lane-reopen-beer-check
```

## 5. 실행 결과

artifact root:

- `docs/experiments/artifacts/exp-237-real-video-lane-reopen-beer-check/`

### 5.1 product_control_motion

- status: `completed`
- prepare mode: `cover_bottom`
- motion avg_rgb_diff: `7.43`
- 관찰:
  - 기존 static control보다 motion 체감은 확실히 올라왔습니다.
  - 다만 본질은 여전히 `controlled zoompan compositor`입니다.
  - 즉 `실제 생성형 영상`을 대체하는 본선 주력이라기보다, fallback/control baseline 역할이 더 정확합니다.

### 5.2 manual_veo

- status: `completed`
- prepare mode: `cover_bottom`
- motion avg_rgb_diff: `16.94`
- 관찰:
  - 맥주 샘플에서는 여전히 체감 품질 upper-bound reference로 강합니다.
  - bottle, foam, liquid 표현이 가장 그럴듯합니다.
  - 다만 이 라인은 production 후보가 아니라 `reference only`라는 전제를 유지해야 합니다.

### 5.3 veo31

- status: `failed`
- elapsed: `1.47s`
- 오류:
  - `429 RESOURCE_EXHAUSTED`
- 해석:
  - 현재 병목은 prompt나 framing이 아니라 quota입니다.
  - 즉 Veo live lane은 지금 상태로는 실험 재개가 불가능합니다.

### 5.4 sora2_current_best

- status: `failed`
- elapsed: `1.16s`
- 오류:
  - `401 invalid_api_key`
- 해석:
  - 현재 병목은 strategy가 아니라 key 상태입니다.
  - 즉 Sora live lane도 지금 상태로는 실험 재개가 불가능합니다.

## 6. scorecard

| 비교군 | 보존성 | 광고 체감 | 반복성 | 서비스 적합성 | 최종 역할 |
| --- | --- | --- | --- | --- | --- |
| `product_control_motion` | pass | hold | pass | pass | fallback baseline |
| `manual_veo` | hold | pass | hold | fail | reference only |
| `veo31` | blocked | blocked | blocked | blocked | blocked by quota |
| `sora2_current_best` | blocked | blocked | blocked | blocked | blocked by key |

## 7. 해석

1. 지금 당장 real video lane이 안 열리는 이유는 `모델이 별로라서`보다 먼저 `provider access`입니다.
2. 따라서 현재 단계에서 prompt phrase나 shot tweak를 더 반복하는 것은 우선순위가 아닙니다.
3. 이미 `manual_veo`가 보여주는 상한선과 `product_control_motion`이 보여주는 control baseline 사이의 갭은 확인됐습니다.
4. 문제는 그 중간을 live provider로 실제 재현할 operational 경로가 지금 막혀 있다는 점입니다.

## 8. 결론

- 이번 실험의 결론은 `real video lane은 필요하지만, 현재는 provider access가 선행 조건`이라는 것입니다.
- 즉 지금 해야 할 일은 다음 순서가 맞습니다.
  1. `OPENAI_API_KEY` 정상화
  2. `Veo` quota 확보
  3. 동일 커맨드로 `맥주`, `규카츠`를 먼저 재실행
- 그 전까지는 `product_control_motion`을 fallback baseline으로 유지하고, `manual_veo`는 계속 quality reference로만 사용합니다.

## 9. 다음 액션

1. 더 이상 local/renderer 미세조정에 시간을 많이 쓰지 않습니다.
2. live provider access를 복구한 뒤 `EXP-237` 커맨드를 그대로 rerun합니다.
3. rerun이 가능해지면 다음 비교는 `맥주 + 규카츠` 2샘플로 확장합니다.
4. 두 샘플 모두에서 `product_control_motion`보다 광고 체감이 높고 보존성 red flag가 없을 때만 실제 영상 생성 lane을 본선 후보로 승격합니다.

## 10. 대표 artifact

- `docs/experiments/artifacts/exp-237-real-video-lane-reopen-beer-check/summary.json`
- `docs/experiments/artifacts/exp-237-real-video-lane-reopen-beer-check/product_control_motion/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-237-real-video-lane-reopen-beer-check/manual_veo/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-237-real-video-lane-reopen-beer-check/sora2_current_best/맥주/prepared_variants/hero_tight_zoom.png`
- `docs/experiments/artifacts/exp-237-real-video-lane-reopen-beer-check/veo31/맥주/prepared_input.png`

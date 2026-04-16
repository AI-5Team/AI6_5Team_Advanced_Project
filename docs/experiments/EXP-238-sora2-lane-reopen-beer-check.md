# EXP-238 Sora 2 Lane Reopen Beer Check

## 1. 기본 정보

- 실험 ID: `EXP-238`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `OpenAI key 복구 후 Sora live lane 재개 / beer single-sample check`

## 2. 왜 이 작업을 했는가

- `EXP-237`에서는 `sora2_current_best`가 `401 invalid_api_key`로 막혀, live Sora 비교를 끝내지 못했습니다.
- 사용자가 `OPENAI_API_KEY`를 새로 교체했다고 알려 주었기 때문에, 가장 먼저 확인해야 할 것은 `전략`이 아니라 `실제 live generation이 다시 도는지`였습니다.
- 이번 작업의 목적은 새 프롬프트를 많이 더 만드는 것이 아니라, `Sora lane이 operational 상태로 복귀했는지`와 `복귀한 결과가 control보다 실제로 나은지`를 single-sample로 빠르게 점검하는 것이었습니다.

## 3. 실험 질문

1. 새 OpenAI 키 기준으로 `sora2_current_best` live generation이 정상 실행되는가
2. `맥주` 샘플에서 current best가 `product_control_motion`보다 광고형 motion 품질을 실제로 올리는가
3. 다음 우선순위는 `두 샘플 확장`인가, 아니면 `prompt phrase 추가`인가

## 4. 실행 조건

### 4.1 샘플

- `맥주`

선정 이유:

- 기존 manual Veo reference 품질이 가장 좋았던 샘플입니다.
- drink lane 기준선도 이미 많이 정리되어 있어, Sora lane 재개 확인용 첫 샘플로 적합합니다.

### 4.2 비교군

- `product_control_motion`
- `sora2_current_best`
- `manual_veo`

### 4.3 실행 커맨드

```bash
python scripts/video_upper_bound_benchmark.py --benchmark-id EXP-238-sora2-lane-reopen-beer-check --providers product_control_motion sora2_current_best manual_veo --images "docs\sample\음식사진샘플(맥주).jpg" --output-dir docs/experiments/artifacts/exp-238-sora2-lane-reopen-beer-check
```

## 5. 실행 결과

artifact root:

- `docs/experiments/artifacts/exp-238-sora2-lane-reopen-beer-check/`

### 5.1 product_control_motion

- status: `completed`
- prepare mode: `cover_bottom`
- mid-frame MSE: `2514.74`
- motion avg_rgb_diff: `7.43`
- 관찰:
  - deterministic compositor답게 결과가 안정적입니다.
  - 오버레이, CTA, 컷 전환이 살아 있어 `광고 패키징 control`로는 여전히 유효합니다.
  - 다만 이 라인은 어디까지나 `motion-composited poster baseline`입니다.

### 5.2 sora2_current_best

- status: `completed`
- elapsed: `94.09s`
- prepare mode: `cover_bottom`
- mid-frame MSE: `2898.03`
- motion avg_rgb_diff: `7.91`
- 관찰:
  - 이번에는 live generation이 정상 완료됐습니다. 즉 `Sora lane` 자체는 다시 열렸습니다.
  - bottle / glass / label 보존은 비교적 괜찮았고, 명백한 중복 오브젝트도 보이지 않았습니다.
  - 하지만 contact sheet 기준 체감은 여전히 `고품질 still + 약한 drift`에 가깝습니다.
  - 수치상 motion은 control과 비슷하지만, 광고형 컷 감각과 패키징은 control보다 강하다고 보기 어렵습니다.

### 5.3 manual_veo

- status: `completed`
- prepare mode: `cover_bottom`
- mid-frame MSE: `5811.95`
- motion avg_rgb_diff: `16.94`
- 관찰:
  - 맥주 샘플에서는 여전히 가장 강한 품질 upper-bound reference입니다.
  - 특히 liquid, foam, glass highlight 표현은 Sora current best보다 설득력이 높습니다.
  - 다만 이 결과는 계속 `비교용 reference only`로만 유지해야 합니다.

## 6. scorecard

| 비교군 | 보존성 | 광고 체감 | 반복성 | 서비스 적합성 | 최종 역할 |
| --- | --- | --- | --- | --- | --- |
| `product_control_motion` | pass | hold | pass | pass | fallback baseline |
| `sora2_current_best` | pass | hold | hold | hold | live candidate, not promoted |
| `manual_veo` | hold | pass | hold | fail | reference only |

## 7. 해석

1. `OPENAI_API_KEY` 복구 후 Sora live lane은 operational 상태로 복귀했습니다.
2. 하지만 `실행이 된다`와 `본선 후보가 된다`는 다른 문제입니다.
3. `맥주` 샘플 기준 current best는 보존성은 괜찮지만, 광고형 motion이나 템플릿 패키징 관점에서 `product_control_motion`을 확실히 넘지 못했습니다.
4. 따라서 지금 단계에서 내릴 수 있는 판단은 `Sora가 다시 비교선에 올라왔다`이지, `본선 승격`은 아닙니다.

## 8. 결론

- 이번 실험의 결론은 두 가지입니다.
  1. `Sora live generation 경로`는 다시 열렸습니다.
  2. 하지만 `맥주 1샘플`만으로는 current best를 production baseline으로 올릴 수 없습니다.
- 따라서 다음 단계는 prompt phrase를 더 늘리는 것이 아니라, 최소한 `맥주 + 규카츠` 2샘플에서 control 대비 판정을 다시 하는 쪽이 맞습니다.

## 9. 다음 액션

1. 같은 benchmark 구조로 `규카츠`를 포함한 2샘플 비교를 수행합니다.
2. 두 샘플 모두에서 `product_control_motion`보다 광고 체감이 높고 preserve red flag가 없어야만 승격 검토를 시작합니다.
3. 만약 샘플별 편차가 크면, 다음 축은 `prompt phrase`가 아니라 `input method` 또는 `hybrid packaging`으로 이동합니다.

## 10. 대표 artifact

- `docs/experiments/artifacts/exp-238-sora2-lane-reopen-beer-check/summary.json`
- `docs/experiments/artifacts/exp-238-sora2-lane-reopen-beer-check/product_control_motion/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-238-sora2-lane-reopen-beer-check/sora2_current_best/맥주/run/맥주/contact_sheet.png`
- `docs/experiments/artifacts/exp-238-sora2-lane-reopen-beer-check/manual_veo/맥주/contact_sheet.png`

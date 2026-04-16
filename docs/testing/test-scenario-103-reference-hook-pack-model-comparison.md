# Test Scenario 103 - reference hook pack model comparison

## 목적

- `EXP-101`에서 같은 reference hook guidance 조건에서 어떤 모델이 더 render-ready한 광고 카피를 내는지 재현합니다.

## 입력 자료

1. `services/worker/experiments/prompt_harness.py`
2. `packages/template-spec/manifests/reference-hook-pack-v1.json`
3. `docs/experiments/EXP-101-reference-hook-pack-cross-provider-model-comparison.md`

## 실행 명령

```bash
python scripts/run_model_comparison_experiment.py --experiment-id EXP-101
```

## 확인 포인트

1. `Gemma 4`, `gpt-5-mini`, `gpt-5-nano`, `Gemini 2.5 Flash` 결과를 비교합니다.
2. 단순 score뿐 아니라 아래를 같이 봅니다.
   - hookText 길이
   - CTA 길이
   - `over_limit_scene_ids`
   - region repeat 문제
   - provider availability

## 기대 결과

1. `Gemma 4`와 `gpt-5-mini`가 상위권으로 남습니다.
2. `gpt-5-mini`는 더 직접적인 톤을 낼 가능성이 큽니다.
3. `Gemma 4`는 format 안정성이 더 좋을 가능성이 큽니다.
4. `gpt-5-nano`는 품질선이 부족할 수 있고, `Gemini 2.5 Flash`는 availability 리스크가 드러날 수 있습니다.

## 판정 기준

- 아래 3개가 모두 맞으면 통과입니다.
  1. 상위 후보가 2개 안팎으로 압축된다
  2. 품질 차이와 운영 리스크가 함께 드러난다
  3. 다음 액션이 repeatability 점검으로 자연스럽게 이어진다

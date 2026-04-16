# Test Scenario 107 - reference hook region anchor budget comparison

## 목적

- `EXP-105`에서 region anchor + length budget을 함께 고정했을 때, Gemma 4와 gpt-5-mini가 어디서 갈리는지 재현합니다.

## 실행 명령

```bash
python scripts/run_model_comparison_experiment.py --experiment-id EXP-105
```

## 기대 결과

1. 두 모델 모두 길이 budget은 어느 정도 따릅니다.
2. Gemma 4는 region anchor를 더 충실하게 따를 가능성이 큽니다.
3. gpt-5-mini는 길이/CTA 직접성은 좋지만 exact region string을 우회할 수 있습니다.

## 판정 기준

- 아래 3개가 모두 맞으면 통과입니다.
  1. 두 모델의 강점이 분리되어 보인다
  2. region anchor 차이가 출력에서 실제로 확인된다
  3. 다음 tuning 방향이 모델별로 나뉜다

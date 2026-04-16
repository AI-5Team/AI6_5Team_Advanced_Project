# Test Scenario 106 - Gemma 4 reference hook urgency/CTA cap

## 목적

- `EXP-104`에서 Gemma 4에 urgency/cta 길이 상한을 넣었을 때 render-ready성이 어떻게 달라지는지 재현합니다.

## 실행 명령

```bash
python scripts/run_prompt_experiment.py --experiment-id EXP-104 --api-key-env GEMINI_API_KEY
```

## 기대 결과

1. candidate variant는 CTA와 urgency를 짧게 만듭니다.
2. over-limit scene은 줄지만, region minimum slot 문제는 남을 수 있습니다.

## 판정 기준

- 아래 3개가 모두 맞으면 통과입니다.
  1. CTA/urgency가 baseline보다 짧아진다
  2. over-limit scene 수가 줄어든다
  3. region 관련 실패가 별도 축으로 남는다는 점이 확인된다

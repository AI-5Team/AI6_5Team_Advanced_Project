# Test Scenario 109 - Gemma 4 benefit 14 char cap

## 목적

- `EXP-107`에서 `Gemma 4`에 benefit 14자 상한을 추가했을 때 headline headroom이 실제로 늘어나는지 확인합니다.

## 입력 자료

1. `scripts/run_prompt_experiment.py`
2. `services/worker/experiments/prompt_harness.py`
3. `docs/experiments/EXP-107-gemma4-benefit-14-char-cap.md`

## 실행 명령

```bash
python scripts/run_prompt_experiment.py --experiment-id EXP-107 --api-key-env GEMINI_API_KEY
```

## 확인 포인트

1. baseline과 candidate 모두 `Gemma 4`로 실행되는지 확인합니다.
2. candidate의 benefit headline 길이가 baseline보다 짧아졌는지 확인합니다.
3. 점수뿐 아니라 hashtag/caption에 nearby landmark 표현이 다시 들어가는지 같이 봅니다.

## 기대 결과

1. benefit headline은 더 짧아집니다.
2. 자동 score 차이는 크지 않을 수 있습니다.
3. 따라서 이 tuning은 `품질 복구`보다 `headroom 확보` 성격으로 해석하는 편이 맞습니다.

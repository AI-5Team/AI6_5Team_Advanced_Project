# Test Scenario 108 - gpt-5-mini exact region caption anchor

## 목적

- `EXP-106`에서 `gpt-5-mini`에 exact region string 제약을 추가했을 때 `성수동` slot hit가 실제로 늘어나는지 확인합니다.

## 입력 자료

1. `scripts/run_prompt_experiment.py`
2. `services/worker/experiments/prompt_harness.py`
3. `docs/experiments/EXP-106-gpt5mini-exact-region-caption-anchor.md`

## 실행 명령

```bash
python scripts/run_prompt_experiment.py --experiment-id EXP-106 --api-key-env OPENAI_API_KEY
```

## 확인 포인트

1. baseline과 candidate 모두 `gpt-5-mini`로 실행되는지 확인합니다.
2. candidate에서 caption 1개와 hashtag 1개에 `성수동` exact string이 들어가는지 확인합니다.
3. 자동 score와 별개로 `서울숲 근처`, `성수역`, `#서울숲근처` 같은 nearby-location leakage가 남는지 수동으로 확인합니다.

## 기대 결과

1. candidate는 최소한 exact region slot hit는 채웁니다.
2. 다만 nearby-location leakage는 여전히 남을 수 있습니다.
3. 따라서 다음 단계가 `평가기 보강` 또는 `후처리 reject`로 이어져야 합니다.

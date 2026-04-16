# Test Scenario 105 - GPT-5 Mini reference hook region/length constraint

## 목적

- `EXP-103`에서 gpt-5-mini에 region/length constraint를 추가했을 때 길이 안정성은 좋아지고, region 조건은 어떤 식으로 깨지는지 재현합니다.

## 실행 명령

```bash
python scripts/run_prompt_experiment.py --experiment-id EXP-103 --api-key-env OPENAI_API_KEY
```

## 기대 결과

1. candidate variant는 over-limit scene을 줄입니다.
2. 대신 region minimum slot을 놓칠 수 있습니다.

## 판정 기준

- 아래 3개가 모두 맞으면 통과입니다.
  1. candidate variant가 baseline보다 짧아진다
  2. over-limit scene 수가 줄어든다
  3. region 관련 실패가 왜 생겼는지 출력에서 확인된다

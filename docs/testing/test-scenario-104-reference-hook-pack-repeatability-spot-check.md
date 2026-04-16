# Test Scenario 104 - reference hook pack repeatability spot check

## 목적

- `EXP-102`에서 `Gemma 4`와 `gpt-5-mini`의 repeatability 차이가 실제로 드러나는지 재현합니다.

## 입력 자료

1. `scripts/run_prompt_repeatability_spot_check.py`
2. `docs/experiments/EXP-102-reference-hook-pack-repeatability-spot-check.md`

## 실행 명령

```bash
python scripts/run_prompt_repeatability_spot_check.py --experiment-id EXP-101 --repeat 3
```

## 확인 포인트

1. 두 모델 모두 같은 prompt variant를 쓰는지 확인합니다.
2. 각 모델의 3회 결과에서 아래를 비교합니다.
   - hookText 변화 폭
   - ctaText 길이
   - over-limit scene 개수
   - region repeat 재발 여부
   - request timeout / availability 문제

## 기대 결과

1. `gpt-5-mini`는 더 짧고 직접적인 카피를 낼 가능성이 큽니다.
2. `Gemma 4`는 hook 구조는 더 안정적일 수 있지만, CTA/urgency 길이나 timeout 이슈가 보일 수 있습니다.
3. 결국 다음 단계가 `constraint tuning`으로 이어져야 한다는 결론이 나옵니다.

## 판정 기준

- 아래 3개가 모두 맞으면 통과입니다.
  1. 두 모델의 흔들림 패턴이 서로 다르게 드러난다
  2. 단순 score 외에 길이/운영 안정성 차이가 보인다
  3. 다음 tuning 방향이 모델별로 분리된다

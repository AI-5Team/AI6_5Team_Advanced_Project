# EXP-145 Gemma Promotion Strict Anchor Transport Profile Check

## 배경

- `EXP-143`, `EXP-144`에서 `Gemma 4`는 single run에서는 각각 `100.0`을 만들었지만, repeatability에서는 `3/3 timeout`으로 모두 실패했습니다.
- 그런데 이전 `EXP-134`에서는 다른 strict prompt 축에서 `Gemma 4`가 기본 60초에서도 안정적으로 통과한 적이 있습니다.
- 따라서 이번에 확인할 질문은 단순했습니다.
  1. 지금 `promotion strict anchor` prompt에서 timeout은 여전히 재현되는가
  2. 된다면 timeout/retry 조정만으로 recover되는가
  3. recover되더라도 품질까지 승격 가능 수준으로 유지되는가

## 목표

- `EXP-144`의 prompt는 그대로 두고 transport profile만 바꿔 `Gemma 4` timeout risk를 다시 확인합니다.
- 같은 prompt에서 아래 3개 profile을 비교합니다.
  - `default_60s_no_retry`
  - `timeout_90s_retry1`
  - `timeout_120s_retry1`

## 고정 조건

- source experiment: `EXP-144`
- source prompt variant: `fixed_promotion_strict_anchor_no_shorter_copy`
- scenario: `scenario-restaurant-promotion-b-grade-real-photo-shorter-copy-off`
- model: `models/gemma-4-31b-it`
- repeat: `3`

## 구현

### 1. 전용 진단 스크립트 추가

- 파일: `scripts/run_gemma_transport_model_comparison_check.py`
- 역할:
  - `model comparison` 실험 정의를 직접 읽음
  - 그중 Google 모델만 골라 transport profile별 repeatability를 비교함
  - deterministic reference / timeout fail count / attempt count / quality score를 같이 artifact로 남김

## 실행

1. compile
   - `python -m py_compile scripts/run_gemma_transport_model_comparison_check.py`
2. transport profile check
   - `python scripts/run_gemma_transport_model_comparison_check.py --experiment-id EXP-144 --repeat 3`

## 결과

- artifact:
  - `docs/experiments/artifacts/exp-145-gemma-promotion-strict-anchor-transport-profile-check.json`

| profile | success | timeout fail | avg score | avg attempts |
|---|---:|---:|---:|---:|
| `default_60s_no_retry` | `2/3` | `1` | `66.7` | `1.0` |
| `timeout_90s_retry1` | `3/3` | `0` | `97.8` | `1.0` |
| `timeout_120s_retry1` | `3/3` | `0` | `97.8` | `1.0` |

sample hook:

- `default_60s_no_retry`
  - `규카츠 할인, 오늘만 맞나요?`
  - `이 혜택, 오늘만 맞나요?`
- `timeout_90s_retry1`
  - `오늘 안 오면 진짜 손해?`
  - `오늘 안 오면 진짜 손해인가요?`
- `timeout_120s_retry1`
  - `오늘 안 오면 손해인가요?`
  - `오늘 안 오면 진짜 손해?`

## 세부 관찰

### 1. 60초 기본 profile

- `1/3`에서 `The read operation timed out`
- 성공한 2회는 모두 `100.0`
- 즉 이 prompt에서 `Gemma 4` 품질 자체보다 먼저 transport ceiling이 발목을 잡고 있었습니다.

### 2. 90초 / retry 1회

- `3/3` 모두 응답 성공
- 하지만 1회에서 `nearby location leaked into strict region budget`
- 누출 surface:
  - `hashtags`
  - `subText`
- 따라서 timeout은 사라졌지만 승격 가능한 품질 `3/3`은 아직 아닙니다.

### 3. 120초 / retry 1회

- `3/3` 모두 응답 성공
- 역시 1회에서 `nearby location leaked into strict region budget`
- 누출 surface:
  - `subText`
- `avg_attempt_count = 1.0`이라 retry는 실제로 작동하지 않았고, 사실상 `timeout 증가`가 핵심이었습니다.

## 해석

1. 현재 `EXP-144` 축에서 `Gemma 4`의 핵심 병목은 "모델이 못 한다"가 아니라 `60초 transport profile`입니다.
2. `90초`만으로 timeout이 사라졌고, `120초`로 더 올려도 품질 이득은 추가로 생기지 않았습니다.
3. 동시에 timeout이 풀려도 `3/3 all pass`는 아니었습니다.
4. 즉 운영 프로필을 늘리면 `Gemma 4`는 다시 실험 가능한 후보가 되지만, 곧바로 option profile 승격 가능한 상태는 아닙니다.

## 판단

- 이 결과로 `Gemma 4`를 `promotion strict anchor` 축에서 바로 제외할 필요는 없어졌습니다.
- 다만 현재 상태를 이렇게 분리해서 보는 편이 맞습니다.
  - 운영 문제: `60초`는 불안정, `90초/retry 1회`면 실험 repeatability는 확보 가능
  - 품질 문제: timeout을 풀어도 `nearby location leakage`가 간헐적으로 남음

## 결론

- `Gemma 4`는 이 축에서 `운영 프로필 조정 후 계속 볼 가치가 있는 모델`입니다.
- 현재 실험 기준 권장 transport는 `90초 / retry 1회`입니다.
- 하지만 baseline 승격 판단은 아직 보류해야 합니다.
- 다음 실험은 transport를 더 건드리는 것이 아니라, `Gemma 4`가 `subText/hashtag`에서 nearby location으로 새는 경로를 한 번 더 잠그는 prompt 보강 쪽이 더 우선입니다.

## 관련 파일

- `scripts/run_gemma_transport_model_comparison_check.py`
- `docs/experiments/artifacts/exp-145-gemma-promotion-strict-anchor-transport-profile-check.json`

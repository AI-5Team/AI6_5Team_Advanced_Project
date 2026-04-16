# EXP-267 Wan 2.1 I2V Micro-LoRA Hold-out Delta Check

## 1. 기본 정보

- 실험 ID: `EXP-267`
- 작성일: `2026-04-15`
- 작성자: Codex
- 목적:
  - `EXP-266`에서 생성한 `1-step` / `2-step` micro-LoRA가 held-out 샘플에서 base 대비 방향성 신호라도 주는지 확인합니다.
  - 단, 이번 목적은 launch-quality 판정이 아니라 **현재 장비에서 base vs adapter 비교 자체가 닫히는지**를 보는 것입니다.

## 2. 먼저 결론

이번 세션에서는 **base vs micro-LoRA held-out 비교를 끝까지 닫지 못했습니다.**

결론은 아래와 같습니다.

1. 비교 스크립트와 실행 경로는 만들었습니다.
2. 하지만 현재 장비에서 `Wan 2.1 I2V-14B-480P` held-out compare는 **inference-only smoke조차 너무 무겁습니다.**
3. 따라서 지금 로컬 장비에서 `base / step001 / step002` 비교를 계속 미는 것은 실익이 작습니다.

즉 `EXP-266`이 보여준 "`학습이 너무 느리다`"에 더해,
이번 `EXP-267`은 **"`비교 inference도 세션 단위로 닫기 어렵다`"**는 점을 추가로 보여줍니다.

## 3. 이번에 실제로 한 일

### 3.1 비교 스크립트 추가

신규 스크립트 `scripts/run_wan21_i2v_micro_lora_holdout_eval.py`를 추가했습니다.

역할은 아래와 같습니다.

1. `EXP-265` manifest의 held-out sample 읽기
2. `Wan-AI/Wan2.1-I2V-14B-480P-Diffusers` base pipeline 로드
3. `EXP-266`의 `step001`, `step002` LoRA를 순차 적용
4. output video / frame / motion metric / preserve metric 비교 summary 저장

## 4. 실행 1: 기준 설정 비교 시도

### 4.1 설정

아래 설정으로 full compare를 먼저 시도했습니다.

- labels:
  - `규카츠`
  - `장어덮밥`
- variants:
  - `base`
  - `step001`
  - `step002`
- frames:
  - `13`
- steps:
  - `8`

### 4.2 관찰

실행 후 아래 현상이 확인됐습니다.

1. process는 살아 있었고 CPU 누적도 증가했습니다.
2. GPU는 계속 `100%` 수준으로 사용됐습니다.
3. output tree에는 `규카츠/base/prepared_input.png`까지만 생겼습니다.
4. `wan21_output.mp4`, `summary.json` 등 최종 artifact는 생성되지 않았습니다.

### 4.3 판단

이 설정은 현재 장비에서 **비교 자체를 세션 안에 닫기 어려운 설정**으로 판단했습니다.

즉 launch-quality에 가까운 비교를 하기도 전에,  
**inference latency 자체가 이미 운영 가능한 수준이 아닙니다.**

## 5. 실행 2: smoke 설정으로 축소 재시도

### 5.1 설정

첫 시도가 너무 무거워 아래처럼 줄여서 다시 시도했습니다.

- labels:
  - `규카츠` 1개만
- variants:
  - `base`
  - `step001`
  - `step002`
- frames:
  - `9`
- steps:
  - `4`

### 5.2 로그 기준 사실

실행 로그에서는 아래까지만 확인됐습니다.

1. base run started
2. model shard loading 완료
3. pipeline component loading 완료
4. 이후에도 최종 output video는 생성되지 않음

실행 artifact 기준으로도 아래만 남았습니다.

- `규카츠/base/prepared_input.png`
- `run.stdout.log`
- `run.stderr.log`

즉 smoke 설정에서도 **첫 base sample조차 final video를 세션 내에 얻지 못했습니다.**

## 6. 이번 결과의 의미

### 6.1 남는 것

1. held-out 비교용 runner는 확보했습니다.
2. base / LoRA adapter 비교 경로도 코드상으로는 정리됐습니다.
3. 따라서 나중에 더 큰 GPU나 cloud 환경이 생기면 같은 runner를 그대로 재사용할 수 있습니다.

### 6.2 이번 세션에서 닫힌 것

아래는 현재 장비 기준으로 사실상 닫힌 판단입니다.

1. `Wan 2.1 I2V-14B local micro-LoRA training`은 너무 느립니다.
2. `Wan 2.1 I2V-14B local held-out adapter compare`도 너무 느리거나 sticky합니다.
3. 즉 현재 장비에서는 **train도 evaluation도 모두 session-friendly하지 않습니다.**

## 7. 최종 판단

이번 세션 기준 최종 판단은 아래와 같습니다.

1. `Wan 2.1 I2V-14B local LoRA` 라인을 지금 장비에서 더 이어가는 것은 우선순위가 아닙니다.
2. `EXP-266`의 학습 gate 실패는 그대로 유지합니다.
3. `EXP-267`은 그 위에 **비교 inference까지도 비실용적**이라는 근거를 추가했습니다.
4. 따라서 현재 본선은 계속 아래가 맞습니다.
   - `template/hybrid + upload assist`

## 8. 다음 액션

다음 액션은 아래로 정리합니다.

1. 로컬 `Wan 2.1 I2V-14B` train/eval 추가 시도 중단
2. `EXP-266`, `EXP-267` artifact와 runner만 보존
3. LoRA 재개 조건을 아래로 제한
   - `24GB+ VRAM`
   - cloud GPU
   - frontier API upper-bound 비교가 먼저 열린 경우

## 9. 산출물

- 스크립트:
  - `scripts/run_wan21_i2v_micro_lora_holdout_eval.py`
- artifact:
  - `docs/experiments/artifacts/exp-267-wan21-i2v-micro-lora-holdout-delta-check/run.stdout.log`
  - `docs/experiments/artifacts/exp-267-wan21-i2v-micro-lora-holdout-delta-check/run.stderr.log`
  - `docs/experiments/artifacts/exp-267-wan21-i2v-micro-lora-holdout-delta-check/규카츠/base/prepared_input.png`

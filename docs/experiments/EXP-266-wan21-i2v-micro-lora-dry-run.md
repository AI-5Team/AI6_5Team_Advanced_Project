# EXP-266 Wan 2.1 I2V Micro-LoRA Dry Run

## 1. 기본 정보

- 실험 ID: `EXP-266`
- 작성일: `2026-04-15`
- 작성자: Codex
- 목적:
  - `EXP-264`에서 정의한 `Wan 2.1 I2V-14B preserve-first micro-LoRA kill test`의 **Gate 1(학습 성립성)** 을 실제로 확인합니다.
  - `EXP-265`에서 고정한 dataset manifest를 finetrainers 학습 포맷으로 export하고, 현재 장비에서 single-GPU dry run이 실제로 성립하는지 확인합니다.

## 2. 먼저 결론

이번 세션에서 확인한 결론은 아래와 같습니다.

1. **로컬 16GB 환경에서 Wan 2.1 I2V-14B micro-LoRA 실행 자체는 성립했습니다.**
2. 다만 **Gate 1 기준은 통과하지 못했습니다.**
3. 실패 이유는 OOM이 아니라 **시간**입니다.

즉 이번 결과는 "`아예 안 돈다`"가 아니라,
**"`돌릴 수는 있지만 현재 장비에서 계속 밀 본선 후보는 아니다`"**에 가깝습니다.

## 3. 이번에 실제로 한 일

### 3.1 training dataset export

`EXP-265` manifest를 finetrainers가 바로 읽을 수 있는 로컬 video dataset 형식으로 export했습니다.

- 신규 스크립트:
  - `scripts/export_exp265_to_finetrainers_dataset.py`
- output root:
  - `docs/experiments/artifacts/exp-266-wan21-i2v-micro-lora-dry-run/`
- 결과:
  - `train_dataset/videos`에 train clip `18개` 복사
  - `prompt.txt`, `videos.txt` 생성
  - `training.json`, `validation.json`, `export_summary.json` 생성

training 설정은 이번 dry run 목적에 맞춰 아래처럼 고정했습니다.

- dataset type: `video`
- resolution bucket: `13 frames / 480 x 832`
- reshape mode: `bicubic`

### 3.2 training toolchain 정비

현재 환경에서 실제 dry run이 가능하도록 toolchain을 맞췄습니다.

- Python:
  - `C:\Users\c\anaconda3\python.exe`
- GPU:
  - `RTX 4080 SUPER 16GB`
- 최종 확인 버전:
  - `torch==2.10.0+cu126`
  - `diffusers==0.37.1`
  - `transformers==4.57.6`
  - `accelerate==1.12.0`
  - `datasets==4.5.0`
  - `peft==0.19.0`
  - `wandb==0.26.0`
  - `torchdata==0.11.0`
  - `kornia==0.8.2`
  - `decord==0.6.0`
  - `torchao==0.17.0`
  - `torchcodec==0.10.0`
  - `ffmpeg==4.3.1`

### 3.3 Windows 로컬 실행용 wrapper 추가

finetrainers 기본 경로만으로는 현재 환경에서 그대로 실행되지 않아, 로컬 wrapper를 추가했습니다.

- `scripts/run_wan21_i2v_micro_lora_dryrun.py`
  - dry run command 작성
  - output/log/meta 관리
- `scripts/wan21_i2v_micro_lora_train_entry.py`
  - Windows 로컬 entrypoint
  - `datasets 4.5.0`가 반환하는 `torchcodec VideoDecoder`를 finetrainers dataset 경로에서 읽을 수 있도록 patch

## 4. 막힌 지점과 실제 조치

### 4.1 `torchcodec` 부재

첫 실행에서는 video decoding 단계에서 바로 실패했습니다.

- 증상:
  - `To support decoding videos, please install 'torchcodec'.`
- 조치:
  - `torchcodec` 설치

### 4.2 `torchcodec 0.11.x` + 현재 torch 조합 불일치

이후에는 `torchcodec` shared library 로딩이 실패했습니다.

- 증상:
  - `Could not load libtorchcodec`
- 해석:
  - 현재 `torch 2.10.0+cu126`와 `torchcodec 0.11.x` 조합이 맞지 않았습니다.
- 조치:
  - `torchcodec`를 `0.10.0`으로 조정
  - `ffmpeg 4.3.1` 설치

### 4.3 `datasets 4.5.0`의 `VideoDecoder` 반환 형식 불일치

그다음에는 finetrainers dataset 경로가 `torchcodec VideoDecoder`를 직접 처리하지 못해 실패했습니다.

- 증상:
  - `'VideoDecoder' object has no attribute 'size'`
- 해석:
  - 현재 `datasets 4.5.0`가 반환하는 객체 형식과 finetrainers v0.2.0 전처리 경로가 바로 맞지 않았습니다.
- 조치:
  - `scripts/wan21_i2v_micro_lora_train_entry.py`에서 dataset preprocess를 로컬 patch
  - `get_frames_in_range()` 기반으로 tensor를 직접 추출하도록 우회

### 4.4 패키지 메타데이터 손상 복구

중간에 `datasets` 버전 조정 시도 중 `packaging`/`certifi` dist-info가 깨져 import 오류가 발생했습니다.

- 조치:
  - 손상된 dist-info 정리 후 재설치
  - 최종 버전:
    - `packaging==26.1`
    - `certifi==2026.2.25`

## 5. 실행 결과

## 5.1 1-step smoke + train step

실행 조건:

- `train_steps=1`
- `gradient_accumulation_steps=8`

결과:

- 실행 성공
- precompute 완료
- step 1 학습 완료
- checkpoint 저장 완료
- LoRA weights 저장 완료

관찰:

- log상 training step 구간:
  - `23:03`
- 전체 종료 기준:
  - `25:59`

즉 "현재 장비에서 Wan 2.1 I2V-14B micro-LoRA가 아예 불가능하다"는 가설은 이번 세션에서 반증됐습니다.

## 5.2 2-step lower-bound run

실행 조건:

- `train_steps=2`
- `gradient_accumulation_steps=1`

이 run은 `gradient_accumulation_steps=8`보다 더 유리한 하한선을 보기 위한 run입니다.

결과:

- 실행 성공
- step 2까지 완료
- checkpoint 저장 완료
- LoRA weights 저장 완료

핵심 로그:

- step 1 시점:
  - `28:41`
  - `grad_norm=0.0245`
  - `global_avg_loss=0.064`
- step 2 완료 시점:
  - `1:08:27`
  - `grad_norm=0.0161`
  - `global_avg_loss=0.0505`
- 전체 종료 기준:
  - `1:11:25`

즉 `gradient_accumulation_steps=1`이라는 더 유리한 조건에서도,
**2 step에 약 71분이 걸렸습니다.**

## 6. Gate 1 판정

`EXP-264`의 Gate 1 기준은 아래였습니다.

- single-GPU에서 `20 training steps`를 안정적으로 완료할 수 있어야 함
- 실패 조건 중 하나:
  - `20 steps`에 `2시간 이상` 소요

### 6.1 사실

이번 세션에서 확인한 사실은 아래입니다.

1. `1 step / grad_acc 8`은 완료
2. `2 step / grad_acc 1`도 완료
3. OOM으로 죽지는 않았음
4. 그러나 가장 유리하게 본 `2 step / grad_acc 1`도 전체 `1시간 11분 25초`가 걸림

### 6.2 추론

이 결과를 기준으로 보면 현재 장비에서 `20 step`은 보수적으로 잡아도 `2시간`을 크게 넘습니다.

- 단순 선형 외삽만 해도 `10시간+` 영역입니다.
- 원래 설계된 `gradient_accumulation_steps=8`로 돌아가면 더 느려집니다.

### 6.3 판정

따라서 이번 실험은 아래처럼 판정합니다.

- **실행 성립 여부:** 성립
- **Gate 1 통과 여부:** 실패
- **실패 원인:** 시간 초과

즉 `LoRA 라인이 OOM 때문에 바로 닫혔다`가 아니라,
**`현재 장비에서 이 실험은 너무 느려서 fail-fast gate를 통과하지 못했다`**가 정확한 결론입니다.

## 7. 이번 결과가 의미하는 것

### 7.1 남는 것

1. `EXP-265` manifest는 실제 학습 입력으로 연결됐습니다.
2. `Wan 2.1 I2V-14B micro-LoRA`는 현재 로컬 장비에서도 **기술적으로는** 실행 가능합니다.
3. 따라서 이후 cloud GPU나 상위 VRAM 환경이 생기면, 같은 dataset과 dry run 경로를 다시 재사용할 수 있습니다.

### 7.2 지금 닫아야 하는 것

1. 현재 `RTX 4080 SUPER 16GB`에서 `20-step` 이상을 계속 밀어보는 일
2. 같은 장비에서 시간을 더 태워 `300-step`으로 가는 일
3. 이 경로를 본선 launch 후보처럼 다루는 일

## 8. 최종 판단

이번 세션 기준 최종 판단은 아래와 같습니다.

1. **이번 LoRA 라인은 "완전 실패"는 아닙니다.**
   - 실행 자체는 성립했고, dataset/entrypoint/log 경로도 확보했습니다.
2. **하지만 현재 장비 기준 continue 실험선은 아닙니다.**
   - `EXP-264`의 fail-fast gate를 이미 시간으로 넘겼습니다.
3. 따라서 현재 저장소의 본선 우선순위는 그대로 유지해야 합니다.
   - `template/hybrid + upload assist`
4. LoRA 라인은 이후 아래 조건 중 하나가 생길 때만 재개하는 것이 맞습니다.
   - `24GB+ VRAM`
   - cloud GPU
   - 더 작은 모델로 실험 질문 자체를 바꿀 때

## 9. 다음 액션

이번 실험 기준 다음 액션은 아래처럼 정리합니다.

1. `Wan 2.1 I2V-14B micro-LoRA` 로컬 20-step 재실행은 중단
2. 이번 artifact와 wrapper를 보존
3. 본선은 계속 `template/hybrid + upload assist`
4. 차후 frontier model access(`Veo 3.1`, `Seedance 2`) 또는 cloud GPU 확보 시 동일 dataset으로 재검토

## 10. 산출물

- 스크립트:
  - `scripts/export_exp265_to_finetrainers_dataset.py`
  - `scripts/run_wan21_i2v_micro_lora_dryrun.py`
  - `scripts/wan21_i2v_micro_lora_train_entry.py`
- artifact:
  - `docs/experiments/artifacts/exp-266-wan21-i2v-micro-lora-dry-run/export_summary.json`
  - `docs/experiments/artifacts/exp-266-wan21-i2v-micro-lora-dry-run/training.json`
  - `docs/experiments/artifacts/exp-266-wan21-i2v-micro-lora-dry-run/validation.json`
  - `docs/experiments/artifacts/exp-266-wan21-i2v-micro-lora-dry-run/run_steps_001/`
  - `docs/experiments/artifacts/exp-266-wan21-i2v-micro-lora-dry-run/run_steps_002/`

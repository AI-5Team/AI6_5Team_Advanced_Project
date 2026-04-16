# EXP-265 Wan 2.1 I2V Micro-LoRA Dataset Prep

## 1. 기본 정보

- 실험 ID: `EXP-265`
- 작성일: `2026-04-15`
- 작성자: Codex
- 목적:
  - `EXP-264`에서 설계한 `Wan 2.1 I2V-14B preserve-first micro-LoRA kill test`의 **Step 1(dataset manifest)** 를 실제로 고정합니다.
  - 동시에 현재 장비에서 **Step 2(20-step dry run)** 로 넘어갈 수 있는지 preflight를 확인합니다.

## 2. 이번에 실제로 한 일

### 2.1 synthetic train pair 생성

신규 스크립트 `scripts/prepare_wan21_i2v_lora_micro_dataset.py`를 추가해 아래를 자동화했습니다.

1. `docs/sample`에서 train 이미지 8장을 읽음
2. 각 이미지마다 preserve-first synthetic clip 2개 생성
3. contact sheet / motion metric / summary를 함께 저장
4. approved hybrid inventory에서 현재 쓸 수 있는 reference clip을 train pair에 제한적으로 추가
5. held-out eval sample 2개(`규카츠`, `장어덮밥`)를 별도 manifest에 기록
6. 현재 Python/GPU/module/ffmpeg 상태를 `preflight.json`으로 저장

### 2.2 실행 결과

- output root:
  - `docs/experiments/artifacts/exp-265-wan21-i2v-micro-lora-dataset-prep/`
- 생성 수량:
  - synthetic train pair: `16`
  - approved reference train pair: `2`
  - total train pair: `18`
  - held-out eval sample: `2`

현재 reference는 `맥주` 2건만 train에 포함됐습니다.

- 이유:
  - approved inventory 전체가 `3건`뿐이고,
  - 그중 `규카츠`는 held-out eval로 남겨야 하므로 train에 넣지 않았습니다.

즉 이번 manifest는 의도적으로 아래처럼 고정했습니다.

- train:
  - `맥주`, `커피`, `라멘`, `타코야키`, `순두부짬뽕`, `아이스크림`, `초코소보로호두과자`, `귤모찌`
  - 각 2개 synthetic pair = `16`
  - 추가 approved reference `맥주` 2개
- eval:
  - `규카츠`, `장어덮밥`

## 3. 관찰

### 3.1 이번 Step 1은 완료

`EXP-264`에서 말한 "dataset manifest 만들기"는 이번 세션에서 실제 artifact까지 포함해 완료했습니다.

이번에 만든 synthetic clip은 모두 deterministic zoompan 기반이라,

- 원본 보존은 강하고
- motion ceiling은 낮습니다.

이 점은 이번 실험의 의도와 맞습니다.  
지금 필요한 것은 "고급 광고 영상 데이터셋"이 아니라,
**LoRA가 preserve bias를 줄 수 있는지 보는 좁은 kill test용 최소 pair**이기 때문입니다.

### 3.2 Step 2는 아직 시작하지 않음

preflight 결과 현재 환경은 아래와 같습니다.

- 사용 Python:
  - `C:\Users\c\anaconda3\python.exe`
- GPU:
  - `RTX 4080 SUPER 16GB`
- 설치 확인:
  - `torch`: 있음
  - `diffusers`: 있음
  - `transformers`: 있음
  - `accelerate`: 있음
  - `ffmpeg/ffprobe`: 있음
  - `finetrainers`: 없음
  - `bitsandbytes`: 없음

즉 현재 상태는 아래처럼 정리됩니다.

- **dataset 준비는 완료**
- **training toolchain은 아직 준비되지 않음**

따라서 `20-step dry run`은 아직 실행하지 않았습니다.

## 4. 냉정한 판단

이번 결과는 의미가 있습니다.

1. `LoRA를 하려면 데이터가 없어서 못 한다` 단계는 넘었습니다.
2. 하지만 `지금 당장 학습을 시작할 수 있다` 단계는 아닙니다.
3. 현재 blocker는 모델 아이디어가 아니라 **training toolchain 부재**입니다.

즉 다음 단계의 핵심은 데이터를 더 늘리는 것이 아니라,

- `finetrainers` 기반으로 실제 single-GPU dry run을 걸 수 있는지
- `bitsandbytes` 없이도 성립하는지, 또는 대체 optimizer 경로로 가야 하는지

를 닫는 것입니다.

## 5. 다음 액션

다음 액션은 `EXP-264` 기준으로 딱 2개뿐입니다.

1. 현재 manifest를 기준 dataset으로 freeze
2. training toolchain을 맞춘 뒤 `20-step dry run` 1회 실행

그 전에는 train pair를 더 늘리지 않습니다.

## 6. 산출물

- 실행 스크립트:
  - `scripts/prepare_wan21_i2v_lora_micro_dataset.py`
- 주요 artifact:
  - `docs/experiments/artifacts/exp-265-wan21-i2v-micro-lora-dataset-prep/manifest.json`
  - `docs/experiments/artifacts/exp-265-wan21-i2v-micro-lora-dataset-prep/preflight.json`

## 7. 결론

- `EXP-264`의 Step 1은 이번 세션에서 실제로 닫았습니다.
- 현재 상태에서 다음 진짜 질문은 오직 하나입니다.

> `finetrainers` 계열 toolchain을 맞춘 뒤,  
> 이 manifest로 `Wan 2.1 I2V-14B micro-LoRA 20-step dry run`이 single GPU 16GB에서 성립하는가?

이 dry run이 안 되면 LoRA 라인은 빠르게 닫는 것이 맞습니다.

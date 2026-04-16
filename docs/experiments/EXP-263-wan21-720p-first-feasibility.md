# EXP-263 Wan 2.1 720p-First Feasibility

## 1. 기본 정보

- 실험 ID: `EXP-263`
- 작성일: `2026-04-14`
- 작성자: Codex
- 목적:
  - `16GB VRAM` 환경에서 `Wan 2.1`이 **광고 품질 판단이 가능한 720p-class 조건**으로 실제로 어디까지 되는지 확인합니다.
  - 이번 실험은 `지금 가능한 것`을 닫기 위한 feasibility check이며, 반복 OVAT가 아닙니다.

## 2. 환경

- GPU: `RTX 4080 SUPER 16GB`
- 시스템 메모리: 약 `64GB`
- 실행 Python: `C:\Users\c\anaconda3\python.exe`
- 핵심 패키지:
  - `torch 2.10.0+cu126`
  - `diffusers 0.37.1`
  - `transformers 4.57.6`
- 실행 스크립트:
  - `scripts/local_video_wan21_first_try.py`

## 3. 왜 720p-first로 했는가

- 480p는 실행 smoke에는 쓸 수 있어도, 광고용 숏폼 품질을 판정하기에는 너무 낮다고 판단했습니다.
- 그래서 이번 실험은 `720p checkpoint / 720p-class area`를 우선으로 고정했습니다.
- 실제 실행 해상도는 Wan 문서의 720-class area를 따르는 `576 x 1024` portrait 기준으로 잡았습니다.

## 4. 실행한 것

### 4.1 Step 1: Wan 2.1 VACE 1.3B

- 목적:
  - `보존과 제어` 문제에 가장 가까운 로컬 후보로서 먼저 확인
- 시도 1:
  - `720p`, `33 frames`, `18 steps`
  - 초기 실행 중 `ftfy` 누락으로 실패
- 시도 2:
  - `720p`, `17 frames`, `8 steps`
  - 1시간 제한 안에서도 완료되지 않았고, GPU는 계속 `100%`에 가깝게 점유됨
  - 산출물은 `prepared_input.png`까지만 남고 최종 video/frame artifact는 생성되지 않음

### 4.2 Step 2: Wan 2.1 T2V 1.3B

- 목적:
  - `motion ceiling 참고용`
- 실행 조건:
  - `576 x 1024`
  - `17 frames`
  - `8 steps`
  - `guidance_scale=5.0`
- 결과:
  - **완료**
  - elapsed: `193.48s`
  - motion metric: `avg_rgb_diff=8.10`
  - preserve metric:
    - first frame `mse=10994.12`
    - mid frame `mse=10993.87`

### 4.3 Step 3: Wan 2.1 I2V 14B 720P + group offloading

- 목적:
  - `16GB`에서 가장 무거운 로컬 보존형 후보가 실제로 끝까지 도는지 확인
- 실행 조건:
  - `576 x 1024`
  - `9 frames`
  - `6 steps`
  - `group offloading`
- 결과:
  - **완료**
  - elapsed: `3216.43s` (약 `53.6분`)
  - motion metric: `avg_rgb_diff=20.19`
  - preserve metric:
    - first frame `mse=162.85`
    - mid frame `mse=237.50`

### 4.4 Step 4: Wan 2.1 I2V 14B 720P + group offloading (`맥주` 재현 샘플)

- 목적:
  - `규카츠` 1회 성공이 우연인지, 다른 샘플에서도 같은 경로가 재현되는지 확인
- 실행 조건:
  - `576 x 1024`
  - `9 frames`
  - `6 steps`
  - `group offloading`
  - 입력 이미지: `음식사진샘플(맥주).jpg`
- 결과:
  - `prepared_input.png` 생성까지는 완료
  - 모델 로드 이후 stderr progress는 `0/6`까지만 찍히고 실제 step 전진 로그 없이 장시간 정지
  - 약 `95분` 관찰 후에도 final video/frame artifact가 생성되지 않아 수동 중단
  - 즉, 같은 설정에서도 샘플에 따라 `완주 시간`이 아니라 `초기 diffusion 단계 체류`부터 불안정할 수 있음을 확인

## 5. 직접 확인한 정성 결과

### 5.1 T2V 1.3B

- contact sheet 기준으로 `규카츠` 원본 보존은 사실상 무너졌습니다.
- 전체적으로 노란색/갈색 계열의 생성 컷으로 재해석됐고, 제품 사진 기반 광고라고 보기 어렵습니다.
- 따라서 이 경로는 `motion ceiling 참고용` 이상으로 올리기 어렵습니다.

### 5.2 I2V 14B offload

- first frame과 mid frame 기준으로는 원본 보존이 상당히 좋았습니다.
- 다만 contact sheet 후반부에서 보라/주황 계열의 이질적 객체/번짐이 끼어드는 장면이 보였습니다.
- 즉 `초반 preserve는 좋지만, clip 전체 안정성은 아직 불안정`한 상태로 판단했습니다.

### 5.3 I2V 14B offload (`맥주` 재현 샘플)

- 이번 샘플은 `품질이 나빴다` 수준 이전에, **생성 시작 자체가 비정상적으로 길어지는 문제**가 드러났습니다.
- `prepared_input.png` 이후 최종 산출물이 전혀 생기지 않았고, stderr progress도 `0/6`에서 더 진행되지 않았습니다.
- 따라서 `I2V 14B offload`는 단순히 “아주 느린 후보”가 아니라, **샘플 의존적 stall 가능성이 있는 불안정 후보**로 보는 것이 맞습니다.

## 6. 사실과 판단

### 6.1 사실

1. `Wan 2.1 VACE 1.3B`는 현재 16GB 환경에서 720 조건 기준 **1시간 내 완료하지 못했습니다**.
2. `Wan 2.1 T2V 1.3B`는 같은 720 조건에서 **완료는 가능**했습니다.
3. `Wan 2.1 I2V 14B 720P + group offloading`도 **완료는 가능**했습니다.
4. 다만 I2V 14B는 `9 frames / 6 steps`의 짧은 설정에서도 **약 53.6분**이 걸렸습니다.
5. 같은 `I2V 14B 720P + group offloading` 경로라도 `맥주` 샘플에서는 약 `95분` 관찰 동안 final artifact를 만들지 못했고, stderr progress는 `0/6`에서 멈춰 있었습니다.

### 6.2 판단

1. `VACE 1.3B`
   - 현재 장비 기준으로는 **로컬 본선 후보로 보기 어렵습니다**.
   - 실행 불가까지는 아니더라도, 지금 workflow에서 쓰기엔 지나치게 느립니다.
2. `T2V 1.3B`
   - **돌아가지만 제품 적합성은 낮습니다.**
   - motion 참고용 이상으로는 의미가 크지 않습니다.
3. `I2V 14B offload`
   - 이번 실험에서 가장 의미 있는 결과이긴 했지만, `규카츠` 1회 성공만으로는 부족했습니다.
   - 즉, **16GB에서도 720-class 보존형 Wan I2V가 “한 번은 완주 가능”**하다는 사실은 확인됐습니다.
   - 그러나 `맥주` 재현 샘플에서 약 `95분` 동안 final artifact가 전혀 생성되지 않았으므로, **운영 시간뿐 아니라 샘플 의존적 stall 리스크까지 크다**고 봐야 합니다.
   - 따라서 현재 본선 후보가 아니라, `reference lane only`로 한 단계 더 낮추는 것이 맞습니다.

## 7. 이번 실험으로 업데이트된 우선순위

### 계속할 것

- `template/hybrid` 본선 유지
- frontier 키 확보 전까지는 `로컬 영상선 재확장` 대신 본선 제품 정리에 집중

### 중단할 것

- `Wan 2.1 VACE 1.3B`를 현재 16GB 로컬 본선 후보로 계속 미는 것
- `Wan 2.1 T2V 1.3B`를 보존형 광고 후보처럼 해석하는 것
- `Wan 2.1 I2V 14B offload`를 반복 실험하면서 본선 후보처럼 다루는 것

### 다음에 할 것

1. 현재 로컬 영상 대안은 `reference lane`으로만 묶고 추가 반복은 중단
2. 이후 key 확보 시:
   - `Seedance 2.0`
   - `Veo 3.1`
   를 같은 benchmark에 투입

## 8. 산출물

- VACE timeout 관찰:
  - `docs/experiments/artifacts/exp-263-wan21-vace-1p3b-720p-gyukatsu-fast/`
- T2V 결과:
  - `docs/experiments/artifacts/exp-263-wan21-t2v-1p3b-720p-gyukatsu-fast/summary.json`
  - `docs/experiments/artifacts/exp-263-wan21-t2v-1p3b-720p-gyukatsu-fast/contact_sheet.png`
- I2V 결과:
  - `docs/experiments/artifacts/exp-263-wan21-i2v-14b-720p-gyukatsu-offload/summary.json`
  - `docs/experiments/artifacts/exp-263-wan21-i2v-14b-720p-gyukatsu-offload/contact_sheet.png`
- I2V 재현 샘플 timeout/stall 관찰:
  - `docs/experiments/artifacts/exp-263-wan21-i2v-14b-720p-beer-offload/`

## 9. 결론

- `16GB라서 Wan 계열은 전부 불가`는 아니었습니다.
- 더 정확한 결론은 아래와 같습니다.
  - `VACE 1.3B`: 현재 조건에서 너무 느림
  - `T2V 1.3B`: 돌아가지만 광고형 보존 후보는 아님
  - `I2V 14B offload`: 720-class, 16GB에서도 완주 사례는 있으나 샘플에 따라 `0/6` 단계 장기 체류가 발생할 수 있음
- 따라서 지금 기준 로컬 영상 대안은 **완전 포기**가 아니라, `I2V 14B offload를 제한적 reference lane으로만 남기되 본선 후보에서는 제외`하는 것이 맞습니다.

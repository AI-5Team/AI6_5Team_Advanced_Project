# EXP-264 Single-Priority LoRA Feasibility Design

## 1. 기본 정보

- 실험 ID: `EXP-264`
- 작성일: `2026-04-15`
- 작성자: Codex
- 성격:
  - `실행 전 설계 문서`
  - `지금 장비와 자원 기준으로 해볼 만한 LoRA/fine-tuning 실험을 단 하나만 고르는 설계`

## 2. 먼저 결론

이번 저장소에서 **LoRA/fine-tuning 실험을 딱 하나만 고른다면**, 아래를 권장합니다.

- **실험명**
  - `Wan 2.1 I2V-14B preservation-first micro-LoRA kill test`
- **목적**
  - `원본 보존`을 유지한 채 `morphing`을 줄일 수 있는지 확인
- **의도**
  - launch-ready 학습이 아니라, **LoRA 라인에 더 투자할 가치가 있는지 빠르게 판정하는 kill test**

즉 이 문서의 제안은 `지금부터 대규모 학습으로 간다`가 아니라,  
**"현재 장비에서 LoRA가 core bottleneck에 의미 있는 신호를 주는가"를 짧게 확인하고, 아니면 바로 닫는다**는 설계입니다.

## 3. 왜 이 실험 하나인가

### 3.1 현재 질문

현재 프로젝트의 핵심 질문은 아래입니다.

1. `원본 사진을 가능한 한 지키면서`
2. `광고로 읽히는 약한 motion`을 만들고
3. `반복 가능한 결과`를 얻을 수 있는가

따라서 지금 필요한 학습 실험은 단순히 “더 멋진 영상이 나오느냐”가 아니라,  
**`원본 보존 문제`에 직접 닿는 실험이어야 합니다.**

### 3.2 후보별 탈락 이유

#### A. `Wan 2.2`

- 공식 문서 기준 `TI2V 5B` 720p도 `최소 24GB VRAM`이 필요합니다.
- 현재 장비는 `RTX 4080 SUPER 16GB`이므로, 지금 기준 후보에서 제외합니다.

#### B. `Wan 2.1 T2V-1.3B LoRA`

- 장비 적합성은 더 높을 수 있습니다.
- 하지만 이 모델은 `image-to-video`가 아니라 `text-to-video`에 가깝고, 현재 핵심 병목인 `원본 보존` 질문에 직접 답하지 못합니다.
- 따라서 **성공해도 본선 질문을 닫지 못하는 실험**입니다.

#### C. `Wan 2.1 VACE-1.3B LoRA`

- 구조적으로는 `보존과 제어` 문제에 더 잘 맞을 수 있습니다.
- 하지만 현재 저장소 기준으로 inference도 이미 무겁고, 공식 저VRAM single-GPU training 경로는 아직 불확실합니다.
- 즉 `지금 당장 장비에서 성립할 가능성`이 가장 불명확합니다.

#### D. `Wan 2.1 I2V-14B full finetuning`

- 현재 장비에서는 사실상 제외입니다.
- 이번 장비/자원 기준에서는 **LoRA 외 full finetuning은 고려하지 않습니다.**

### 3.3 그래서 남는 것

- `원본 보존` 질문에 직접 닿고
- 현재 오픈 툴링에서 지원 신호가 있으며
- full finetuning보다 훨씬 가벼운 방법으로 접근할 수 있는 경로는
- **`Wan 2.1 I2V-14B LoRA`**뿐입니다.

단, 이 경로도 **"성공 가능성이 높다"가 아니라 "질문에 가장 직접 답하는 단 하나의 카드"**라는 뜻입니다.

## 4. 현재 실제 자원 vs 이상적 자원

### 4.1 현재 실제로 가진 것

1. 하드웨어
   - `RTX 4080 SUPER 16GB`
   - 시스템 RAM 약 `64GB`
2. 모델 실행 경험
   - `Wan 2.1 I2V-14B 720P + group offloading`은 1회 완주
   - 다만 다른 샘플에서는 `0/6` stall이 발생
3. 입력 자산
   - `docs/sample`의 음식/음료 샘플 이미지
4. 내부 비디오 자산
   - `docs/experiments/artifacts` 아래 다수의 mp4 artifact
   - 다만 quality-labeled, preserve-safe, rights-clear paired data는 매우 제한적
5. 승인 inventory
   - `EXP-255` summary 기준 승인된 hybrid inventory는 총 `3건`뿐입니다.
   - 즉 “괜찮다”고 확정된 source clip은 아주 적습니다.

### 4.2 이상적이지만 현재 없는 것

1. `24GB+ VRAM` 또는 cloud GPU
2. 수십~수백 건의 `실제 음식 광고 paired clip`
3. rights-clear dataset
4. 반복 실험을 감당할 예산과 시간

### 4.3 의미

따라서 이번 LoRA 설계는 아래를 전제로 해야 합니다.

- **대규모 일반화 학습은 불가**
- **좁은 질문을 보는 micro-LoRA kill test만 가능**

## 5. 실험 목표와 비목표

### 5.1 목표

아래 질문에 답하는 것이 목표입니다.

> `Wan 2.1 I2V-14B`에 아주 작은 preserve-first LoRA를 얹으면,  
> 현재 base model 대비 `음식 원본 보존`과 `morphing 억제`가 실제로 나아지는가?

### 5.2 비목표

이번 실험은 아래를 목표로 하지 않습니다.

1. launch-ready 모델 만들기
2. 모든 음식 카테고리에 일반화되는 모델 만들기
3. 본선 교체
4. 장시간 학습 최적화

## 6. 학습 데이터 설계

## 6.1 원칙

현재 저장소에 **고품질 paired video dataset이 충분히 없습니다.**

그래서 이번 실험은 아래 2종을 섞습니다.

1. **synthetic preserve clips**
   - 현재 deterministic renderer / product_control_motion에서 만든 약한 motion clip
   - 장점: 원본 보존은 거의 완벽
   - 단점: motion ceiling이 낮음
2. **approved/reference clips**
   - 승인 inventory나 수동 검토에서 살아남은 clip
   - 장점: 더 그럴듯한 motion 힌트 제공
   - 단점: 수량이 매우 적음

즉 이번 LoRA는 “고품질 광고영상 학습”이 아니라,  
**`원본 보존 regularizer + 약한 motion prior`**를 주는 실험으로 봐야 합니다.

## 6.2 데이터 구성 제안

### train split

- 이미지 `8장`
  - `맥주`
  - `커피`
  - `라멘`
  - `타코야키`
  - `순두부짬뽕`
  - `아이스크림`
  - `초코소보로호두과자`
  - `귤모찌`
- 각 이미지당 synthetic preserve clip `2개`
  - `product_control_motion` 약한 push-in
  - `product_control_motion` 다른 framing variant
- approved/reference clip `최대 3개` 추가
  - 현재 inventory에 있는 `맥주`, `규카츠` 등 소수 clip만 제한적으로 사용

### validation split

- 이미지 `2장`
  - `규카츠`
  - `장어덮밥`

이 둘은 train에서 제외하고, **held-out preserve test**로만 씁니다.

## 6.3 데이터 수량

- train pair 목표: `16 ~ 19 clip`
- validation pair 목표: `2 clip`

이보다 더 늘리는 순간 현재 장비에서 학습 시간이 급격히 늘고,  
현재 데이터 품질로는 정보량도 크게 늘지 않습니다.

## 7. 모델/학습 방식

### 7.1 선택

- base model: `Wan 2.1 I2V-14B`
- 방법: **LoRA only**
- full finetuning: `하지 않음`

### 7.2 학습 해상도

- training:
  - `480-class portrait`
  - 이유: 현재 장비에서 720p training은 비현실적일 가능성이 큼
- evaluation:
  - `720p-first benchmark`
  - 이유: launch-quality 판단은 여전히 720p에서 해야 함

즉 이번 실험은 아래를 의미합니다.

- **학습은 480-class feasibility**
- **판정은 720p benchmark**

## 7.3 clip 설정

- training frame 수: `9 ~ 13 frames`
- fps: `8`
- 길이: `약 1.1 ~ 1.6초`

이유:

- 지금 질문은 긴 광고 영상을 만드는 것이 아니라,  
  **LoRA가 preserve 방향으로 기울 수 있느냐**를 보는 것입니다.
- 길이를 길게 잡으면 현재 장비에서는 학습 자체가 무너질 가능성이 큽니다.

## 7.4 LoRA 범위

- target:
  - `Wan transformer attention projections only`
- freeze:
  - `VAE`
  - `text encoder`
  - `image encoder`

이유:

- 16GB에서는 가능한 한 adaptation 범위를 좁혀야 합니다.
- 이번 실험은 “전체 모델을 바꾸는 것”이 아니라,  
  **보존 관련 generation behavior에 작은 bias를 주는 것**이 목적입니다.

## 7.5 하이퍼파라미터 초안

- rank: `8`
- alpha: `16`
- dropout: `0.05`
- batch size: `1`
- gradient accumulation: `8`
- max steps: `300`
- learning rate: `5e-5`
- optimizer:
  - `8-bit optimizer` 우선
- 기타:
  - `gradient checkpointing`
  - `precomputed latents/conditions` 사용 우선

## 8. 왜 이 설계가 현재 장비 기준 최선인가

1. `원본 보존` 질문에 직접 답합니다.
2. full finetuning보다 훨씬 가볍습니다.
3. 현재 실제 자산만으로도 최소한의 dataset을 만들 수 있습니다.
4. 실패해도 “LoRA가 이 문제를 지금 장비/데이터로는 못 푼다”는 결론을 얻을 수 있습니다.

즉 이 실험은 **성공보다 실패했을 때도 정보량이 큰 설계**입니다.

## 9. 반드시 넣어야 할 fail-fast gate

이번 실험은 아래 3개를 넘기지 못하면 바로 종료합니다.

### Gate 1. 학습 성립성

- 기준:
  - single-GPU에서 `20 training steps`를 안정적으로 완료할 수 있어야 함
- 실패 조건:
  - OOM 반복
  - offload 포함해도 step 진행 불가
  - `20 steps`에 `2시간 이상` 소요

### Gate 2. held-out preserve 개선

- 비교 대상:
  - base model vs LoRA model
- 샘플:
  - `규카츠`
  - `장어덮밥`
- 실패 조건:
  - first/mid frame MSE가 의미 있게 줄지 않음
  - morphing 체감이 줄지 않음

### Gate 3. motion collapse 방지

- 실패 조건:
  - preserve는 좋아졌지만 사실상 still image 수준으로 무너짐
  - `avg_rgb_diff`가 base 대비 지나치게 떨어짐

## 10. 성공/실패 판정 기준

### 성공

아래 3개를 동시에 만족할 때만 “다음 단계 검토 가능”으로 봅니다.

1. held-out 2샘플 모두에서 preserve metric 개선
   - 목표: `mid-frame MSE 20% 이상 개선`
2. morphing 감소가 육안으로 확인됨
3. motion metric이 base 대비 `20% 이상 악화되지 않음`

### 실패

아래 중 하나면 이번 라인은 종료합니다.

1. 학습 자체가 성립하지 않음
2. preserve 개선이 held-out에서 재현되지 않음
3. preserve를 얻는 대신 motion이 완전히 죽음
4. synthetic clip에만 맞고 실제 reference clip에는 효과 없음

## 11. 실행 순서

1. dataset manifest 만들기
   - train 16~19 pair
   - validation 2 pair
2. `20-step dry run`
3. dry run 통과 시 `300-step max` 학습
4. held-out 2샘플 `720p benchmark` 비교
5. 결과 문서화 후 continue/stop 결정

## 12. 이번 설계에서 중요한 냉정한 판단

### 12.1 이 실험이 풀 수 있는 것

- LoRA가 `원본 보존` 쪽으로 bias를 주는지
- 지금 장비에서 single-GPU micro-LoRA가 성립하는지

### 12.2 이 실험이 못 푸는 것

- 고품질 광고 motion 전체
- 대규모 일반화
- 상위 상용 모델 upper-bound 대체

즉 이 실험이 성공해도 곧바로 “출시 가능”이 되는 것은 아닙니다.

## 13. 최종 권고

이번 저장소와 현재 장비 기준으로 LoRA/fine-tuning 실험을 단 하나만 고른다면 아래가 맞습니다.

1. **`Wan 2.1 I2V-14B preserve-first micro-LoRA`를 딱 1회만 한다**
2. synthetic preserve clip + 소수 approved clip만 쓴다
3. 학습이 안 되거나 held-out에서 효과가 없으면 **LoRA 라인은 바로 닫는다**

즉,

- `될 때까지 계속`이 아니라
- **`지금 장비로 의미가 있는지 판정하는 마지막 좁은 실험`**

으로 다뤄야 합니다.

## 14. 다음 액션

이번 문서 기준 다음 액션은 아래 3개뿐입니다.

1. dataset manifest 후보 수집
2. `20-step dry run` 가능 여부 확인
3. dry run 실패 시 즉시 종료

그 전에는 새 후보를 더 늘리지 않습니다.

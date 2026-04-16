# Execution Priority And Model Candidates

## 1. 목적

- 현재 자원 조건에서 `지금 바로 해볼 수 있는 것`과 `키 확보 후 열 후보`를 분리합니다.
- 목표는 후보를 무한히 늘리는 것이 아니라, **같은 질문을 반복하지 않으면서도 남은 가능성은 닫는 것**입니다.
- 이 문서는 새 실험 결과가 아니라, 다음 실행 우선순위를 고정하기 위한 기획/운영 문서입니다.

## 2. 먼저 결론

- **지금 당장 계속 밀어야 하는 본선**은 `template/hybrid 광고 패키징 + upload assist`입니다.
- **현재 자원 기준으로 추가 검증해볼 가치가 남은 로컬 영상 후보**는 `Wan 2.1`의 일부 경로뿐입니다.
- **키 확보 후 frontier 후보로 올려둘 모델**은 `Seedance 2.0`, `Veo 3.1`입니다.
- 반대로 `Wan 2.2`, `LTX 추가 OVAT`, `Sora single-photo prompt/crop/edit 반복`은 현재 우선순위에서 내립니다.

## 3. 사실과 추론

### 3.1 확인된 사실

1. 현재 저장소가 가장 안정적으로 제공하는 결과물은 `product_control_motion + hybrid overlay + caption/package + upload assist`입니다.
2. 현재 자원 기준 상용 비디오 실사용 경로는 사실상 `OpenAI key 기반 Sora lane`뿐입니다.
3. 저장소 내부 기록상 Sora는 `single-photo + preserve image` 조건에서 일관된 production baseline을 만들지 못했습니다.
4. `Wan 2.1`은 공식 문서 기준으로 다음이 확인됩니다.
   - `T2V 1.3B`는 consumer-grade 구간에 들어가며, Diffusers 메모리 최적화 예시는 약 `13GB VRAM` 수준입니다.
   - `I2V 14B`는 기본적으로 매우 무겁고, 공식 메모리 최적화 문서도 base inference를 `최대 35GB VRAM` 수준으로 설명합니다.
   - 다만 `group offloading`을 쓰면 `14GB VRAM` 수준까지 낮출 수 있다고 안내합니다. 대신 느리고 CPU RAM 사용량이 큽니다.
5. `Wan 2.2`는 공식 GitHub 기준으로 `TI2V 5B`도 `최소 24GB VRAM`이 필요합니다.
6. `Veo 3.1`은 공식 문서 기준으로 image-to-video, first/last frame, reference asset image(일부 preview) 등을 지원하고, 비용/쿼터가 분명한 유료 후보입니다.
7. `Seedance 2.0`은 공식 문서 기준으로 멀티모달 입력(다수 이미지/비디오/오디오)과 editing/extend 흐름을 제공하는 frontier 후보입니다.

### 3.2 추론

1. 현재 프로젝트 병목은 `예쁜 영상`보다 `원본 보존 + 광고 문법 + repeatability`이므로, 단순 one-shot I2V보다 **참조/제어 입력이 많은 모델**이 더 유리할 가능성이 큽니다.
2. 그 관점에서는 키 확보 후 탐색 우선순위를 `Seedance 2.0 -> Veo 3.1` 순으로 두는 것이 합리적입니다.
3. 다만 실제 채택은 가격표가 아니라, **같은 benchmark에서 원본 보존과 repeatability를 통과하는지**로 결정해야 합니다.

## 4. 현재 자원 기준 실행 우선순위

### P0. 제품 본선 유지 및 실험 가드 고정

이 항목은 바로 진행합니다.

- 유지:
  - `template/hybrid 광고 패키징`
  - `upload assist`
  - `결과 패키지(video/post/caption/hashtags)`
- 금지:
  - LTX 추가 OVAT
  - Sora single-photo prompt/crop/edit 반복
  - baseline 미확정 상태에서의 운영 레이어 추가 확장

## 5. 현재 자원 기준 로컬 후보

### 5.1 1순위 로컬 후보: Wan 2.1 VACE 1.3B

- 이유:
  - 현재 프로젝트 문제는 자유 생성보다 `보존과 제어`에 가깝습니다.
  - Wan 계열 중에서도 VACE는 control-to-video, image/video-to-video, subject/composition 계열을 포함해 제어성이 더 맞습니다.
- 판정:
  - **현재 16GB 환경에서 가장 먼저 짧게 확인해볼 로컬 후보**
- 실행 원칙:
  - 1회성 feasibility check로만 진행
  - **품질 판정용 run은 720p 우선**
  - 짧은 길이, 제한된 샘플 2개만 사용
  - 통과 못 하면 바로 종료
  - 480p는 품질 판단용이 아니라, `왜 720p가 안 되는지` 분리하는 smoke check로만 사용

### 5.2 2순위 로컬 후보: Wan 2.1 T2V 1.3B

- 이유:
  - 공식 문서 기준 메모리 구간이 가장 현실적입니다.
  - 다만 이 모델은 본 프로젝트의 핵심인 `사진 보존형 광고 숏폼`과 직접 일치하지는 않습니다.
- 판정:
  - **motion ceiling 참고용**
  - 제품 본선 후보가 아니라, “16GB에서 로컬 영상이 어디까지 가능한가” 확인용입니다.
- 실행 원칙:
  - 품질 판단에 쓸 run은 가능하면 720p를 우선 시도
  - 만약 이 경로가 720p에서 의미 있는 결과를 못 내면, 해당 결과는 quality evidence로 쓰지 않음

### 5.3 3순위 조건부 후보: Wan 2.1 I2V 14B 720P + group offloading

- 이유:
  - 공식 문서에 group offloading으로 VRAM을 낮추는 경로가 존재합니다.
  - 실제 로컬 실행에서도 `576 x 1024`, `9 frames`, `6 steps` 조건으로 한 번은 완주했습니다.
- 조건:
  - CPU RAM이 충분히 크고
  - 처리시간이 길어도 감수할 수 있을 때만
- 판정:
  - **reference lane only**
  - 한 번 완주 사례는 있지만, 재현 샘플(`맥주`)에서는 약 `95분` 동안 final artifact를 만들지 못하고 `0/6` 단계 장기 체류가 확인됐습니다.
  - 즉, 매 세션 반복 돌릴 본선 후보가 아니라 `기술적 가능성 기록용`에 가깝습니다.
- 수정 원칙:
  - **광고 품질 판정은 720p 우선**으로 진행
  - 720p offload 경로가 샘플별로 안정적으로 재현되지 않으면, 그 사실 자체를 `현 하드웨어 기준 비현실적`이라는 근거로 기록
  - 완주 사례 1건만으로 본선 가능성 판단으로 승격하지 않음

### 5.4 현재 제외: Wan 2.2

- 이유:
  - 공식 문서 기준 현재 16GB 환경과 맞지 않습니다.
- 판정:
  - **지금은 후보 목록에서 제외**

## 6. 현재 자원 기준 상용 후보

### 6.1 Sora lane

- 현재 자원에서 열려 있는 유일한 상용 비디오 후보입니다.
- 다만 지금까지의 저장소 기록상 같은 `single-photo + preserve image` 질문을 반복해도 새 정보가 거의 나오지 않았습니다.

### Sora 운영 원칙

- 허용:
  - **새로운 입력 제어 방식**이 생겼을 때의 제한적 검증
- 금지:
  - prompt phrase 반복
  - crop 반복
  - 같은 edit path 재반복

즉, **Sora는 “계속 깎는 본선”이 아니라 “새 control signal이 생길 때만 열리는 보류 후보”로 다뤄야 합니다.**

## 7. 키 확보 후 frontier 후보

### 7.1 1순위 frontier 후보: Seedance 2.0

- 이유:
  - 공식 소개 기준 멀티모달 입력 폭이 넓습니다.
  - 현재 병목인 `원본 보존 + 광고 제어` 문제와 구조적으로 더 잘 맞을 가능성이 있습니다.
- 기대 포인트:
  - 다중 참조 이미지/비디오 기반의 보존 개선 가능성
  - edit/extend 흐름과의 결합 가능성
- 주의:
  - 현재 우리 자원에는 포함돼 있지 않습니다.
  - 가격과 사용량은 공식 문서 기준으로 다시 확인하면서 들어가야 합니다.

### 7.2 2순위 frontier 후보: Veo 3.1

- 이유:
  - 시각적 quality upper-bound 후보입니다.
  - first/last frame, image-to-video, reference asset 이미지 등으로 비교적 강한 기능을 제공합니다.
- 기대 포인트:
  - raw visual quality 상한 확인
  - 현재 manual upper-bound와 실제 API lane의 차이 확인
- 주의:
  - 비용/쿼터 부담이 분명합니다.
  - 저장소 내부 과거 기록상 manual Veo는 보존 실패 사례가 이미 있었습니다.

## 8. 추천 benchmark 순서

### 8.1 지금 즉시

1. `template/hybrid` 본선 유지
2. `Wan 2.1 VACE 1.3B` 짧은 feasibility check
3. `Wan 2.1 T2V 1.3B` motion ceiling check
4. 필요할 때만 `Wan 2.1 I2V 14B 720P offload` 1회성 확인

### 8.2 키 확보 후

1. `Seedance 2.0`
2. `Veo 3.1`

## 9. 공통 합격 기준

모든 후보는 아래 4개 기준으로만 통과/실패를 판정합니다.

1. 원본 보존
   - 음식, 로고, QR, 텍스트, 구도 변형이 치명적이지 않은가
2. 광고형 motion
   - 단순 still drift가 아니라 광고로 읽히는가
3. repeatability
   - 같은 입력에서 결과 편차가 과하지 않은가
4. usable cost
   - 클립 1개를 실서비스에서 감당 가능한 비용/시간으로 만들 수 있는가

## 9.1 해상도 판정 원칙

- **광고 품질 판단용 benchmark는 720p 우선**으로 고정합니다.
- 이유:
  - 480p는 “실행 가능 여부”를 보는 데는 쓸 수 있어도, 광고용 숏폼 품질을 판정하기에는 너무 낮을 수 있습니다.
- 따라서 아래처럼 구분합니다.
  1. `720p 성공`:
     - 품질/보존/repeatability 판정 가능
  2. `720p 실패 + 480p 성공`:
     - 기술적 smoke는 통과했지만, launch-quality evidence로는 미채택
  3. `720p 실패 + 480p도 실패`:
     - 현재 하드웨어/경로 기준 후보 제외

## 10. 실행 제안

### 10.1 지금 바로 할 것

1. `Wan 2.1` 로컬 검증 레인을 새로 열되, **후보를 3개 이하로 제한**
2. benchmark 샘플도 `보존이 어려운 2개`만 사용
3. quality benchmark는 `720p-first`로 고정
4. `I2V 14B offload`가 두 번째 샘플에서 stall하면, reference lane으로만 남기고 본선 후보에서 바로 제외

### 10.2 문서/운영 측면에서 같이 할 것

1. `완전 자동 광고 숏폼 생성`과 `하이브리드 광고 패키징 도구`를 문서상 분리
2. frontier 후보는 `future candidate track`으로 명시
3. 키 확보 전에는 후보 이름만 올려두고, 접근 가능해지는 순간 같은 benchmark로 비교

## 11. 이번 문서 기준 최종 판정

- **지금 가능한 것을 다 해본다**는 말은, 가능한 모든 실험을 계속 늘린다는 뜻이 아닙니다.
- 이 문서에서의 의미는 아래와 같습니다.
  - 현재 자원으로 새 정보를 줄 수 있는 후보만 짧게 닫는다.
  - 반복 질문은 멈춘다.
  - frontier 후보는 키 확보 후 같은 기준으로 다시 연다.

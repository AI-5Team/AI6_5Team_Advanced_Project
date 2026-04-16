# EXP-39 Midpoint Direction Review

## 1. 기본 정보

- 실험 ID: `EXP-39`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `중간 점검 / 실험 방향 재정렬`

## 2. 왜 이 작업을 했는가

- 로컬 텍스트/비디오 실험이 충분히 쌓였기 때문에, 지금 방향이 기획 의도와 계속 맞는지 다시 점검할 필요가 있었습니다.
- 특히 현재 연구가 `서비스 본선`을 강화하는지, 아니면 `연구 자체`로 새고 있는지 확인해야 했습니다.

## 3. 기준 문서

- `docs/planning/01_SERVICE_PROJECT_PLAN.md`
- `docs/planning/03_CONTENT_PIPELINE_AND_TEMPLATE_SPEC.md`
- `docs/planning/06_EVALUATION_TEST_AND_OPERATIONS.md`
- `HISTORY.md`

## 4. 중간 판단

### 4-1. 지금까지 맞게 진행된 부분

1. `단일 벤더/단일 모델 고정 금지` 방향은 기획과 맞습니다.
   - 계획 문서는 `Gemma 4`를 포함한 후보군 비교를 명시하고 있고, 실제로 `OpenAI`, `Google`, `HF`, `Ollama` 비교 경로를 열었습니다.
2. 로컬 비디오 후보를 `Wan2.2-I2V-A14B`, `LTX-2.3`에서 바로 확정하지 않고, 현재 장비 기준 실현 가능 경로를 찾은 것은 맞는 접근입니다.
   - `LTX-Video 2B / GGUF`와 `CogVideoX-5B-I2V` first try까지 간 것은 “실험 모듈”의 feasibility를 줄이는 작업으로 유효했습니다.
3. 실험 문서화와 artifact 축적은 충분히 잘 되고 있습니다.

### 4-2. 지금 드리프트가 생기기 쉬운 부분

1. 기획의 핵심 제작 방식은 여전히 `템플릿 기반 숏폼 조합`입니다.
   - 계획 문서는 생성형 비디오를 `메인 기능이 아닌 실험 모듈`로 둡니다.
   - 따라서 `LTX`, `CogVideoX` 연구가 주력 구현 라인을 대체하기 시작하면 기획에서 벗어납니다.
2. 현재는 `generation research`가 빠르게 전진한 반면, `quick action -> change set`, `업로드/업로드 보조`, `첫 결과물 생성 시간`, `스타일 식별성` 같은 Phase 1 KPI 검증은 상대적으로 덜 전진했습니다.
3. EXAONE 쪽 프롬프트 레버는 이미 diminishing return이 보입니다.
   - `region repeat`, `hashtag/caption budget`은 연속 실패했습니다.
   - 여기서 같은 식의 prompt phrasing 실험을 더 반복하는 것은 효율이 낮습니다.

### 4-3. 현재 전체 판단

1. 전체 방향이 완전히 틀어진 것은 아닙니다.
2. 다만 현재는 `서비스 본선 강화`보다 `생성 연구` 쪽 비중이 조금 더 커진 상태입니다.
3. 따라서 다음부터는 아래처럼 lane을 분리해야 합니다.

## 5. 다시 정렬한 lane

### Lane A. 서비스 본선

- 목적: `Phase 1 MVP`를 기획 문서대로 완성
- 기준:
  - 템플릿 기반 생성
  - quick action visible delta
  - 결과 패키징
  - 업로드/업로드 보조
  - KPI 및 사용자 테스트 재현성

### Lane B. 생성 연구선

- 목적: `실험 모듈` 후보 검증
- 기준:
  - 모델 비교
  - 로컬/오픈소스 실행성
  - 프롬프트/가드레일 개선
  - 생성형 비디오 품질 비교

### 운영 원칙

1. Lane B 결과가 좋아도 바로 본선 승격하지 않습니다.
2. 본선 승격 조건은 아래 4개입니다.
   - 템플릿/결과 패키지와 연결 가능
   - 5~7초 메시지 전달 안정성
   - 실행 시간/실패율이 데모 허용 범위
   - CTA/상품 가시성/가독성 기준 통과

## 6. 지금 시점의 우선순위 재정렬

### 바로 계속해야 할 것

1. `LTX`는 연구선 1순위 유지
   - 현재 로컬 비디오 후보 중 가장 낫습니다.
   - 다음 OVAT는 `steps`가 아니라 `prompt length` 또는 `num_frames`
2. 텍스트 쪽은 `EXAONE prompt phrasing`보다 `guardrail/postprocess` 검토가 더 적절
3. `Gemma3 12B`, `gpt-5-mini`, `Gemma 4` 같은 상대적으로 유망한 모델군 비교는 유지

### 다시 끌어올려야 할 것

1. `quick action`이 실제 결과 차이를 얼마나 만드는지 end-to-end 검증
2. `scenePlan -> render -> package -> history/result` 연결 상태 점검
3. `instagram` 업로드 또는 업로드 보조 흐름 검증
4. `첫 결과물 생성 시간`, `스타일 식별성`, `지역 적합도` 같은 KPI 측정

### 지금 줄여야 할 것

1. EXAONE에 대한 세부 프롬프트 phrasing 실험 반복
2. 생성형 비디오를 곧바로 제품 baseline처럼 취급하는 해석
3. scene-lab 같은 별도 surface를 장기간 본선처럼 다루는 작업

## 7. 결론

- 현재 방향은 **부분적으로 맞고, 부분적으로 과열된 연구선이 섞인 상태**입니다.
- 지금 가장 건강한 정렬은:
  - `서비스 본선`은 템플릿 기반 MVP 완성
  - `생성 연구선`은 LTX 중심으로 제한된 OVAT
- 즉 앞으로는 `연구를 멈추는 것`이 아니라, `연구선과 본선을 섞지 않는 것`이 핵심입니다.

## 8. 다음 액션

1. 다음 생성 연구는 `LTX + prompt length` 한 레버 실험으로 진행
2. 동시에 서비스 본선 점검으로 `quick action visible delta`와 `업로드 보조 흐름` 검증을 다시 올림
3. 생성형 비디오를 본선으로 승격할지 여부는 별도 ADR 기준으로 판단

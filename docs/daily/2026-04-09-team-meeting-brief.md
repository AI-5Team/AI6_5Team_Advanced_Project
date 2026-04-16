# 2026-04-09 팀 회의 브리핑

## 0. 회의 시작 30초 요약

- 저는 처음부터 연구만 한 것이 아니라, `템플릿 기반 숏폼 생성 서비스`의 본선 루프를 먼저 만들고 그 위에서 prompt, model, video 실험을 쌓아 왔습니다.
- 다만 최근에는 `local LTX video baseline` 실험 비중이 커지면서 본선 제품 완성도보다 연구선이 앞서가기 시작했습니다.
- 그래서 오늘 기준 결론은 `새 실험 확대`보다 `본선 제품 루프 복귀`가 우선이라는 점입니다.

## 1. 핵심 메시지

1. 서비스의 출발점은 `사진 몇 장으로 숏폼 + 게시글 + 캡션 세트까지 빠르게 만드는 도구`였습니다.
2. 지금까지의 실험은 대부분 무의미한 우회가 아니라, 품질 한계와 차별화 포인트를 찾기 위한 과정이었습니다.
3. 하지만 최근 구간에서는 `video baseline 연구`가 본선 구현보다 앞서간 것이 사실입니다.
4. 그래서 지금은 `새로운 실험을 더 늘리는 시점`이 아니라 `본선 제품 루프를 닫는 시점`입니다.

## 2. 서비스 원래 목표

- 대상 사용자: 소상공인, 특히 카페/음식점 운영자
- 해결하려는 문제:
  - 사진은 있지만 홍보용 숏폼이나 게시글을 빠르게 만들기 어렵다
  - 게시 전 준비물과 캡션 작업까지 같이 번거롭다
- 우리가 만들려던 핵심 흐름:
  - 업로드/입력
  - 템플릿 기반 생성
  - 결과 확인
  - quick action 재생성
  - 게시 또는 업로드 보조
  - history 재진입

## 3. 왜 지금까지 이런 흐름으로 왔는지

### Phase 1. 먼저 제품 뼈대를 만들었습니다

- API, worker, web, contracts, template-spec를 먼저 잡았습니다.
- 이 단계에서 이미 `생성 -> 결과 -> publish/assist -> history`의 큰 루프는 만들어졌습니다.

### Phase 2. prompt 품질을 먼저 보정했습니다

- deterministic copy만으로는 표현력이 부족해서 prompt harness를 붙였습니다.
- 대표 실험은 `EXP-01`, `EXP-02`였습니다.
- 이 시기 기준 텍스트 baseline은 `Gemma 4`였습니다.

### Phase 3. 차별화 포인트를 B급 숏폼으로 보기 시작했습니다

- 단순 문구 생성만으로는 차별화가 약하다고 판단해서 `B급 감성 영상/레이아웃` 쪽을 파기 시작했습니다.
- `EXP-03`~`EXP-06`에서 flyer layout, owner-made safe zone, hand-drawn reference를 실험했습니다.

### Phase 4. renderer baseline이 약하다는 문제를 만났습니다

- 레버 실험보다 먼저 결과물 baseline을 재구축해야 한다고 판단했습니다.
- 그래서 `EXP-07`~`EXP-13`에서 Pillow 결과물, linebreak, HTML/CSS compositor, frame capture를 재정비했습니다.

### Phase 5. 연구가 본선과 분리되지 않도록 다시 연결했습니다

- renderer spike가 제품과 따로 놀지 않게 `scenePlan bridge`를 worker/result/history에 연결했습니다.
- `EXP-14`~`EXP-22`는 이 연결을 다지는 구간이었습니다.

### Phase 6. 특정 모델에 고정되지 않게 비교 범위를 넓혔습니다

- Google, OpenAI, Hugging Face, Ollama를 모두 비교했습니다.
- `EXP-23`~`EXP-31`은 provider/model 비교와 output constraint 점검 구간이었습니다.

### Phase 7. 로컬 비디오가 실제로 가능한지 확인했습니다

- 현재 장비인 `RTX 4080 Super 16GB`에서 실제로 돌아갈 수 있는 비디오 후보를 좁혔습니다.
- `EXP-32`, `34`, `36`, `38`, `39`에서 feasibility matrix와 first try를 확인했습니다.

### Phase 8. 최근에는 LTX deep dive 비중이 너무 커졌습니다

- 한편으로는 quick action, publish/assist, history guard를 보강했습니다.
- 하지만 다른 한편으로는 `prepare_mode`, `framing`, `tray/drink/beer lane` 중심의 LTX micro OVAT가 길게 이어졌습니다.
- 이 구간이 바로 지금 방향이 조금 샌 지점입니다.

### Phase 9. 오늘 기준으로 다시 정렬했습니다

- `EXP-87`에서 지금 방향이 서비스 기획과 맞는지 감사를 했습니다.
- 그 결과 바로 이어서 아래 복귀 작업을 진행했습니다.
  - `EXP-88`: result/history actual media preview 복구
  - `EXP-89`: upload assist action UX 보강
  - web contracts/template-spec canonical spec 정리 시작

## 4. 지금까지 써 본 모델 정리

### 텍스트 생성

- 규칙형 baseline
  - deterministic `_build_copy_bundle()`
- Google / Gemma
  - `models/gemma-4-31b-it`
  - `models/gemini-2.5-flash`
  - `models/gemini-2.5-flash-lite`
- OpenAI
  - `gpt-5-mini`
  - `gpt-5-nano`
  - `gpt-4.1-mini`
- Hugging Face / 오픈소스
  - `Qwen/Qwen3-4B-Instruct-2507`
  - `Qwen/Qwen3.5-27B`
- 로컬 Ollama
  - `gemma3:12b`
  - `exaone3.5:7.8b`
  - `llama3.1:8b`
  - `mistral-small3.1:24b-instruct-2503-q4_K_M`

### 비디오 생성

- feasibility 검토
  - `Wan2.2-I2V-A14B`
  - `Wan2.2-TI2V-5B`
  - `LTX-2.3 / LTX-2`
  - `Mochi 1 Preview`
- 실제 실행
  - `LTX-Video 2B GGUF`
  - `CogVideoX-5B-I2V`

## 5. 실험 기록을 팀 회의 기준으로 묶어서 말하면

- `EXP-01`~`02`
  - prompt OVAT 시작
  - deterministic copy의 한계를 보완할 baseline 마련
- `EXP-03`~`06`
  - B급 감성 방향 탐색
  - 서비스 차별화 포인트 확인
- `EXP-07`~`13`
  - renderer baseline 재구축
  - HTML/CSS compositor 가능성 확인
- `EXP-14`~`22`
  - scenePlan bridge
  - 연구 결과를 본선 루프와 재연결
- `EXP-23`~`31`
  - Google / OpenAI / HF / Ollama 모델 비교
- `EXP-32`~`39`
  - local video feasibility, first try
- `EXP-41`~`62`
  - quick action, publish/assist, history guard 등 제품 루프 강화
- `EXP-64`~`86`
  - LTX prepare_mode / framing / tray-drink-beer micro OVAT
  - 여기서 최근 연구선 비중이 과해졌습니다
- `EXP-87`~`89`
  - 현재 방향 감사
  - 본선 제품 루프 복귀 시작

## 6. 지금 상태를 냉정하게 보면

### 맞게 가고 있는 부분

- 본선 서비스 루프는 이미 살아 있습니다.
- quick action visible delta가 실제로 확인되었습니다.
- publish/assist fallback과 variant guard도 어느 정도 정리되어 있습니다.
- scenePlan bridge는 연구선을 본선에 다시 연결한 좋은 작업이었습니다.

### 방향이 샌 부분

- 최근에는 `local LTX baseline` 미세 조정이 너무 길어졌습니다.
- 특히 `tray / drink / beer / prompt phrase / prepare_mode` 쪽은 연구로는 의미 있었지만, 현재 제품 우선순위를 앞질렀습니다.
- 결과적으로 지금 팀이 당장 써볼 수 있는 제품 완성도보다 비디오 baseline 탐구에 시간이 더 많이 들어간 상태였습니다.

## 7. 오늘 기준으로 이미 되돌린 것

### 1. result/history actual preview 복구

- 이제 result/history에서 실제 `video`, `post` 결과물을 다시 직접 볼 수 있습니다.

### 2. upload assist action UX 보강

- 이제 assist 패키지에서 바로 아래 행동을 할 수 있습니다.
  - 영상 열기
  - 영상 다운로드
  - 게시글 열기/다운로드
  - 캡션 복사
  - 해시태그 복사
  - 전체 복사
  - 업로드 순서 안내

### 3. canonical spec 정리 시작

- web이 `@ai65/contracts`, `packages/template-spec`을 직접 기준으로 읽기 시작했습니다.
- 즉 web 내부의 별도 하드코딩 기준선을 줄이는 작업을 시작했습니다.

## 8. 결정 필요 사항

### 합의 1. 당분간 무엇을 우선할지

- 선택지:
  - 새 LTX OVAT를 계속 넓힌다
  - 본선 제품 루프 정리로 우선 복귀한다
- 제안:
  - `본선 제품 루프 정리`를 먼저 하겠습니다.

### 합의 2. 연구선을 어떻게 운영할지

- 선택지:
  - LTX micro OVAT를 계속 빠르게 확장한다
  - local video 연구는 유지하되 속도를 낮추고 baseline만 관리한다
- 제안:
  - `연구는 유지하되 baseline 정리 수준으로 속도를 낮추겠습니다.`

### 합의 3. 다음 검증을 어디에 둘지

- 선택지:
  - 기술 실험을 더 한다
  - 브라우저 QA와 실제 운영 시나리오 검증을 붙인다
- 제안:
  - `브라우저 QA와 문제 적합성 검증을 먼저 붙이겠습니다.`

## 9. 다음 우선순위 제안

### 1순위. 본선 결과 확인 흐름을 더 닫기

- result/history/upload assist를 실제 사용자 관점에서 끝까지 점검해야 합니다.
- 지금은 기능이 살아났지만, 실제로 팀이 써보고 막히는 지점을 더 줄여야 합니다.

### 2순위. canonical spec 정리 계속하기

- worker, web, contracts, template-spec 기준선을 더 단일화해야 이후 실험도 덜 샙니다.

### 3순위. local video 연구선은 정리 위주로 유지하기

- 아예 버릴 필요는 없지만, 당분간은 `새 미세 OVAT 확장`보다 `현재 baseline 정리`가 맞습니다.

## 10. 결론 정리

- “우리는 제품을 안 만들고 연구만 한 게 아니라, 제품 루프를 먼저 만들고 그 위에서 실험을 쌓아 왔습니다.”
- “다만 최근에는 local video baseline 쪽이 너무 커져서, 오늘 기준으로는 다시 본선 제품 루프로 복귀하는 게 맞다고 정리했습니다.”
- “이미 result/history preview, upload assist UX, canonical spec 정리는 시작했고, 다음은 이 본선 루프를 더 닫는 작업을 우선하려고 합니다.”

## 11. 회의 중 참고 문서

- 전체 흐름을 더 길게 설명한 문서:
  - `docs/daily/2026-04-09-meeting-full-trajectory-summary.md`
- 오늘 세부 작업 로그:
  - `docs/daily/2026-04-09-codex.md`
- 방향 재정렬 근거:
  - `docs/experiments/EXP-87-current-direction-review-and-priority-reset.md`

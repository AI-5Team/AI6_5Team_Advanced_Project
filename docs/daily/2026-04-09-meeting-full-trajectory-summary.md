# 2026-04-09 회의용 전체 경과 정리

## 1. 이 문서의 목적

- 이번 문서는 `기획 배포 이후 첫 전체 공유 회의`를 위한 정리본입니다.
- 단순히 “오늘 무엇을 했는가”가 아니라, 아래를 한 번에 설명할 수 있도록 정리했습니다.
  - 이 서비스가 원래 무엇을 만들려고 했는가
  - 왜 지금 같은 실험 흐름이 생겼는가
  - 지금까지 어떤 모델/실험군을 써 봤는가
  - 어디까지는 맞게 왔고, 어디서부터 비중이 기울었는가
  - 지금 기준으로 무엇을 계속하고 무엇을 줄여야 하는가

## 2. 원래 서비스 기획 의도

### 기획의 본선

- 대상: 소상공인, 특히 카페/음식점
- 핵심 문제: 사진 몇 장만으로 SNS용 숏폼/게시글/캡션 세트를 빠르게 만들고, 게시까지 이어지는 작업 부담을 줄이는 것
- 본선 UX:
  - 생성 마법사
  - 결과 확인
  - quick action 재생성
  - 게시 또는 업로드 보조
  - history 재진입

### 처음부터 분명했던 점

1. 메인은 `템플릿 기반 운영형 서비스`입니다.
2. 생성형 비디오는 본선의 품질을 올릴 수 있는 연구선이지만, 서비스 전체를 대신하는 목적은 아닙니다.
3. 즉 “연구”는 필요하지만, 최종 목표는 `서비스 루프를 닫는 것`입니다.

## 3. 지금까지 어떻게 여기까지 왔는가

## 3-1. Phase 1 구현 부트스트랩

### 한 일

- `packages/contracts`, `packages/template-spec` 초안 정리
- `services/api` FastAPI + SQLite/local filesystem runtime 구현
- `services/worker` preprocess / deterministic copy generation / Pillow+FFmpeg render / publish fallback 구현
- `apps/web` 생성 마법사 / 상태 polling / 결과 / quick action / SNS 연결 / assist fallback / history / account center 구현

### 의미

- 이 시점에서 이미 서비스 본선 루프의 뼈대는 생겼습니다.
- 즉 “아무것도 없는 상태에서 연구만 한 것”은 아니고, 처음엔 제품 루프를 먼저 세웠습니다.

## 3-2. Prompt 실험 시작

### 왜 시작했는가

- deterministic `_build_copy_bundle()` 기준선은 빨리 동작하지만, 문구 품질과 제약 준수에 한계가 있었습니다.
- 그래서 production은 건드리지 않고, `prompt_harness`로 실험 경로를 분리했습니다.

### 초반 핵심 실험

- `EXP-01`: slot guidance
- `EXP-02`: audience/tone guidance

### 이 단계의 결론

- `Gemma 4`는 초기 텍스트 실험 baseline으로 의미가 있었습니다.
- prompt 레버를 한 번에 하나씩 바꾸는 OVAT 방식도 이때 자리 잡았습니다.

## 3-3. B급 감성/영상 방향으로 전환

### 왜 전환했는가

- 기획 차별화 포인트를 `B급 감성 숏폼`으로 더 강하게 가져가려는 판단이 있었습니다.
- 그래서 실험 우선순위가 카피 미세조정보다 영상 생성/레이아웃으로 이동했습니다.

### 주요 실험

- `EXP-03`: B급 flyer/poster layout
- `EXP-04`: owner-made safe zone
- `EXP-05`: 손그림 reference + 실제 음식 사진
- `EXP-06`: service-aligned promotion opening priority

### 이 단계의 결론

- 단순히 자극적인 B급 스타일만 강화하면 상품 가시성이 깨진다는 점을 확인했습니다.
- 이후 “스타일 탐색”보다 “서비스 목적 전달”이 더 중요하다는 기준으로 재정렬했습니다.

## 3-4. Renderer baseline 재구축

### 왜 다시 갈아엎었는가

- 초기 Pillow 기반 결과물은 OVAT를 계속하기 전에 baseline 자체가 너무 약했습니다.
- 그래서 `레버 비교`보다 `renderer/layout baseline rebuild`가 먼저라는 결론이 나왔습니다.

### 주요 실험

- `EXP-07`: structured_bgrade_v2 baseline rebuild
- `EXP-08`: linebreak / multi-photo validation
- `EXP-09`: renderer strategy pivot options
- `EXP-10`~`EXP-13`: HTML/CSS scene-lab, frame capture, scene budget, hierarchy polish

### 이 단계의 결론

- Pillow handcrafted 결과물은 제품 baseline으로 채택하지 않기로 했습니다.
- 대신 HTML/CSS compositor + scene-based 구조가 더 유망하다는 쪽으로 넘어갔습니다.

## 3-5. ScenePlan bridge와 서비스 루프 재연결

### 왜 중요했는가

- renderer spike가 길어지면 제품 루프와 분리될 위험이 있었기 때문입니다.

### 주요 실험

- `EXP-14`: worker scene-plan bridge
- `EXP-15`~`EXP-19`: service-aligned prompt levers
- `EXP-20`: template lever comparison + scene-plan web bridge
- `EXP-21`: project result scenePlan direct bridge
- `EXP-22`: history scenePlan preview

### 이 단계의 결론

- 연구 결과가 다시 worker/result/history 화면으로 들어오기 시작했습니다.
- 이 구간은 “좋은 연구”로 봐도 됩니다. 연구가 본선과 다시 연결됐기 때문입니다.

## 3-6. 모델 비교 구간

### 왜 했는가

- 특정 모델 하나에만 고정하지 말고, 실제 사용 가능한 후보를 넓게 보려는 목적이었습니다.

### 실제 사용/시도한 텍스트 모델

#### 규칙형 baseline

- deterministic `_build_copy_bundle()`

#### Google / Gemma 계열

- `models/gemma-4-31b-it`
- `models/gemini-2.5-flash`
- `models/gemini-2.5-flash-lite`

#### OpenAI 계열

- `gpt-5-mini`
- `gpt-5-nano`
- `gpt-4.1-mini`
  - 시도했지만 당시 key 문제로 비교 실패 기록이 있습니다.

#### Hugging Face / 오픈소스 경로

- `Qwen/Qwen3-4B-Instruct-2507`
- `Qwen/Qwen3.5-27B`

#### 로컬 Ollama 경로

- `ollama:gemma3:12b`
- `ollama:exaone3.5:7.8b`
- `ollama:llama3.1:8b`
- `ollama:mistral-small3.1:24b-instruct-2503-q4_K_M`

### 모델 비교 관련 실험

- `EXP-23`: cross-provider comparison
- `EXP-24`: Google family comparison
- `EXP-25`: OpenAI available models comparison
- `EXP-26`: review template model comparison
- `EXP-27`: gpt-5-mini output constraint
- `EXP-28`: Gemini 2.5 Flash strict JSON constraint
- `EXP-29`: Hugging Face open-source text comparison
- `EXP-30`: local Ollama comparison
- `EXP-31`, `EXP-33`, `EXP-35`: EXAONE 로컬 레버 실험

### 이 단계의 중간 결론

1. `Gemma 4`는 안정성 baseline 역할을 했습니다.
2. `gpt-5-mini`는 속도/품질 타협 후보로 의미가 있었습니다.
3. `gpt-5-nano`는 빠르지만 scene budget 안정성이 약했습니다.
4. `Gemini 2.5 Flash`는 당시 형식 안정성 이슈가 컸습니다.
5. 로컬 텍스트 후보 중에서는 `EXAONE 3.5 7.8B`, `Gemma3 12B`가 비교적 유망했습니다.

## 3-7. 로컬 비디오 모델로 이동

### 왜 이동했는가

- 서비스 차별화 포인트를 실제 생성형 비디오 baseline까지 연결해 보려는 목적이었습니다.
- 동시에 현재 장비(`RTX 4080 Super 16GB`)에서 돌아가는 후보를 좁히는 작업도 필요했습니다.

### feasibility 수준에서 검토한 비디오 모델

- `Wan2.2-I2V-A14B`
- `Wan2.2-TI2V-5B`
- `LTX-2.3 / LTX-2`
- `LTX-Video 2B distilled / GGUF / FP8`
- `CogVideoX-5B-I2V`
- `Mochi 1 Preview`

### 실제 사용/실행한 비디오 모델

- `city96/LTX-Video-gguf` + `Lightricks/LTX-Video`
- `THUDM/CogVideoX-5b-I2V`

### 관련 실험

- `EXP-32`: local video feasibility matrix
- `EXP-34`: LTX preflight
- `EXP-36`: LTX first try
- `EXP-38`: CogVideoX first try
- `EXP-39`: midpoint direction review

### 이 단계의 결론

1. 현재 장비에서는 `LTX-Video 2B GGUF`가 가장 현실적인 로컬 비디오 baseline이었습니다.
2. `CogVideoX-5B-I2V`는 실행은 됐지만 속도/품질이 현재 기준으론 불리했습니다.
3. `Wan2.2-I2V-A14B`, `LTX-2.3`는 팀이 이미 접해 본 모델이지만, 이 저장소 기준 local baseline 1순위는 아니었습니다.

## 3-8. LTX deep dive와 본선 검증이 섞인 구간

### 제품 루프 관련 실험

- `EXP-41`: shorter copy visible delta
- `EXP-43`: highlight price visible delta
- `EXP-45`: generation timing and upload assist flow
- `EXP-47`: publish route matrix
- `EXP-49`: instagram permission error fallback UI
- `EXP-50`, `EXP-53`, `EXP-55`, `EXP-57`: history publish state visibility 강화
- `EXP-59`: result-to-publish package consistency
- `EXP-60`: stale variant guard
- `EXP-62`: cross-project variant guard

### LTX parameter / prompt deep dive

- `EXP-37`, `EXP-40`, `EXP-42`, `EXP-44`, `EXP-46`, `EXP-48`, `EXP-51`, `EXP-52`, `EXP-54`, `EXP-56`, `EXP-58`, `EXP-61`, `EXP-63`

### category / framing / prepare-mode 계열

- `EXP-64`~`EXP-72`

### 최근 tray / drink / beer micro OVAT

- `EXP-73`~`EXP-86`

### 이 구간의 의미

- 좋은 쪽:
  - quick action delta
  - publish/assist guard
  - history UX 보강
  - baseline 운영 규칙 정리
- 비중이 커진 쪽:
  - drink/tray/beer 미세 OVAT
  - prompt phrase / framing / prepare_mode classifier 미세 조정

즉 이 구간은 `서비스에 도움 된 실험`과 `연구 비중이 과해진 실험`이 함께 섞여 있습니다.

## 3-9. 오늘 기준 방향 재정렬

### 오늘 한 일

- `EXP-87`: 현재 진행 방향 감사
- `EXP-88`: result/history 실제 media preview 복구
- `EXP-89`: upload assist action UX
- 그리고 web의 `contracts`, `template-spec` 기준선 단일화 작업 진행

### 오늘 결론

1. 지금까지의 흐름은 완전히 잘못된 것은 아닙니다.
2. 하지만 최근에는 `local video baseline 연구`가 본선보다 앞서간 상태였습니다.
3. 따라서 지금 우선순위는 `새 실험 추가`보다 `본선 구현/검증 복귀`가 맞습니다.

## 4. 지금 기준으로 사용해 본 모델/실험군 정리

## 4-1. 텍스트 생성 모델

### 실제 실행됨

- deterministic rule-based baseline
- `models/gemma-4-31b-it`
- `models/gemini-2.5-flash`
- `models/gemini-2.5-flash-lite`
- `gpt-5-mini`
- `gpt-5-nano`
- `Qwen/Qwen3-4B-Instruct-2507`
- `ollama:gemma3:12b`
- `ollama:exaone3.5:7.8b`
- `ollama:llama3.1:8b`
- `ollama:mistral-small3.1:24b-instruct-2503-q4_K_M`

### 시도했지만 실패/제약 기록이 명확한 것

- `gpt-4.1-mini`
  - 초기 key 문제
- `Qwen/Qwen3.5-27B`
  - provider timeout
- `models/gemini-2.5-flash`
  - format 안정성 실패 구간이 분명히 있었음

## 4-2. 비디오 생성 모델

### feasibility 검토

- `Wan2.2-I2V-A14B`
- `Wan2.2-TI2V-5B`
- `LTX-2.3 / LTX-2`
- `Mochi 1 Preview`

### 실제 실행

- `LTX-Video 2B GGUF`
- `CogVideoX-5B-I2V`

## 5. 실험 기록 전체를 어떻게 요약할 것인가

아래처럼 설명하면 회의에서 흐름이 자연스럽습니다.

### Phase A. 제품 뼈대 구현

- API, worker, web, template-spec, contracts를 먼저 세웠다.

### Phase B. prompt 개선

- deterministic baseline 한계를 보완하려고 `Gemma 4` 중심 prompt OVAT를 시작했다.

### Phase C. B급 영상 방향 탐색

- B급 감성, owner-made layout, hand-drawn reference, service-aligned opening 구조를 실험했다.

### Phase D. renderer 재구축

- Pillow baseline이 약해 HTML/CSS scene-lab과 scene-plan bridge로 넘어갔다.

### Phase E. 모델 비교

- Google / OpenAI / HF / Ollama까지 넓게 후보를 봤다.

### Phase F. 로컬 비디오 baseline

- 현재 장비에서 가능한 비디오 모델을 좁혀 `LTX`를 중심으로 baseline을 만들었다.

### Phase G. 제품/연구 혼합 구간

- quick action, publish/assist, history 보강과 LTX 미세 OVAT가 동시에 쌓였다.

### Phase H. 오늘 재정렬

- 연구 비중이 앞서간 것을 인정하고, result/history/upload assist/product contract 기준선부터 다시 닫고 있다.

## 6. 지금 기준 핵심 baseline

## 6-1. product / service baseline

- 템플릿 기반 숏폼 + 게시글 + 캡션 세트
- quick action 재생성
- publish / assist fallback
- history 재진입

## 6-2. prompt / model baseline

- production 기본은 아직 deterministic
- 연구 후보는 `Gemma 4`, `gpt-5-mini`
- review/promotion 템플릿별 상위 레버는 일부 정리됨

## 6-3. local video baseline

- tray/full-plate: `cover_center + no steam`
- drink general phrase: `still life beverage shot`
- top-heavy drink: `cover_top`
- bottom-heavy bottle+glass: `cover_bottom`

다만 이 baseline은 아직 `서비스 baseline`이 아니라 `연구 baseline`입니다.

## 7. 지금 팀에 공유해야 할 핵심 메시지

1. 처음에는 제품 본선을 먼저 만들었고, 그 위에서 실험을 쌓아 왔습니다.
2. 실험 자체는 의미가 있었지만, 최근에는 local video baseline 쪽 비중이 커졌습니다.
3. 오늘부터는 다시 `본선 서비스 루프 복구/정리` 쪽으로 우선순위를 옮기고 있습니다.
4. 이미 result/history preview, upload assist action UX, contracts/template-spec 기준선 단일화는 시작했습니다.
5. 다음 단계는 새 LTX OVAT를 더 늘리는 것이 아니라, 남은 local alias 정리와 브라우저 실사용 QA, 그리고 문제 적합성 검증입니다.

## 8. 회의에서 바로 말하기 좋은 결론

- “우리는 처음부터 제품을 안 만들고 연구만 한 게 아니라, 제품 뼈대를 먼저 만들고 그 위에서 prompt/model/video 연구를 붙여 왔습니다.”
- “중간부터 생성형 비디오 baseline이 너무 재미있고 의미가 있어서 그쪽 비중이 커졌는데, 오늘 기준으로는 다시 본선 서비스 루프로 복귀하는 게 맞다고 정리했습니다.”
- “지금은 result/history/upload assist와 canonical spec 정리를 다시 닫고 있고, 로컬 비디오 연구는 baseline 정리 수준으로 유지하려고 합니다.”

## 9. 같이 보면 좋은 문서

- `HISTORY.md`
- `docs/daily/2026-04-07-codex.md`
- `docs/daily/2026-04-08-codex.md`
- `docs/daily/2026-04-09-codex.md`
- `docs/experiments/EXP-87-current-direction-review-and-priority-reset.md`
- `docs/experiments/EXP-88-product-result-media-preview-reconnect.md`
- `docs/experiments/EXP-89-upload-assist-action-ux.md`

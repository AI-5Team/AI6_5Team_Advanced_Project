# EXP-259 Launch Direction Reassessment

## 1. 기본 정보

- 실험 ID: `EXP-259`
- 작성일: `2026-04-14`
- 작성자: Codex
- 성격: `새 생성 실험이 아니라 기획-구현-실험-자원 조건을 다시 심판하는 방향성 감사 문서`

## 2. 목적

- 이 저장소가 처음 기획한 `광고 생성 서비스`, 특히 `사진 몇 장으로 광고용 숏폼 영상을 생성한다`는 약속에 아직 정렬되어 있는지 다시 점검했습니다.
- 이번 문서의 목표는 새 모델을 더 붙이거나 새 실험을 늘리는 것이 아니라, `지금 방향이 출시로 이어질 수 있는가`를 냉정하게 판정하는 것입니다.
- 특히 아래 네 가지를 분리해서 판단했습니다.
  1. 현재 비전 그대로의 출시 가능성
  2. scope를 줄였을 때의 출시 가능성
  3. 현재 실제 자원 조건에서 가능한가
  4. 상위 모델 접근이 열린다고 가정하면 무엇이 달라지는가

## 3. 검토 범위

### 3.1 내부 문서

- `HISTORY.md`
- `docs/planning/README.md`
- `docs/planning/01_SERVICE_PROJECT_PLAN.md`
- `docs/planning/03_CONTENT_PIPELINE_AND_TEMPLATE_SPEC.md`
- `docs/planning/06_EVALUATION_TEST_AND_OPERATIONS.md`
- `docs/planning/08_DOCUMENTATION_POLICY.md`
- `docs/adr/*`
- `docs/experiments/*`
- `docs/testing/*`
- `docs/daily/*`

### 3.2 내부 코드

- `services/worker/pipelines/generation.py`
- `services/worker/renderers/*`
- `services/worker/experiments/*`
- `services/api/*`
- `scripts/*`
- `packages/template-spec/*`
- `packages/contracts/*`
- `apps/web/src/components/*`
- `apps/web/src/app/*`
- `apps/web/src/lib/*`

### 3.3 외부 최신 사실 확인 출처

- OpenAI Sora 2 모델/가격 문서: <https://developers.openai.com/api/docs/models/sora-2>, <https://developers.openai.com/api/docs/pricing>
- Google Gemini API / Vertex AI Veo 문서:
  - <https://ai.google.dev/gemini-api/docs/pricing>
  - <https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/veo/3-1-generate>
  - <https://cloud.google.com/vertex-ai/generative-ai/pricing>
- BytePlus / Seedance 문서:
  - <https://docs.byteplus.com/en/docs/ModelArk/1544106?redirect=1>
  - <https://seed.bytedance.com/en/blog/official-launch-of-seedance-2-0>
  - <https://docs.byteplus.com/id/docs/ModelArk/1541595?redirect=1>

## 4. 확인된 사실

### 4.1 기획 본선은 원래부터 `템플릿 기반 광고 패키징`이었습니다

- 기획 문서는 핵심 제작 방식을 `템플릿 기반 영상 조합 우선`으로 두고, 생성형 비디오는 메인 기능이 아니라 실험 모듈로 분리합니다.
- 핵심 산출물도 `숏폼 1종 + 게시글 1종 + 캡션 세트 + 업로드/업로드 보조`이며, 자유 프롬프트 기반 크리에이티브 툴을 목표로 하지 않습니다.
- 즉 원래 비전의 본선은 `고품질 생성 모델 그 자체`가 아니라 `광고 결과물을 반복 생산하는 서비스 루프`였습니다.

### 4.2 이미 닫힌 baseline과 아직 닫히지 않은 baseline이 분명히 갈립니다

- 닫힌 쪽:
  - 카피 baseline은 prompt baseline freeze와 coverage audit을 거치며 사실상 정리됐습니다.
  - deterministic / shot-aware renderer baseline도 `product_control_motion`과 hybrid overlay packaging을 포함한 서비스 경로까지 올라왔습니다.
  - 업로드 -> 생성 -> 결과 -> quick action -> 게시/업로드 보조 루프는 API, worker, web에 모두 살아 있습니다.
- 닫히지 않은 쪽:
  - local/open-source video baseline은 `preserve는 되지만 near-static`이라는 한계를 넘지 못했습니다.
  - `sora2_current_best`는 live path가 다시 열렸지만, 내부 기록상 두 샘플에서 일관된 production baseline이 아니었습니다.
  - `manual_veo`는 품질 upper-bound reference로는 의미가 있었지만, 원본 보존과 QR/텍스트/구성 유지에는 실패 사례가 남았습니다.

### 4.3 최근 흐름은 `생성 품질 개선`보다 `hybrid 운영화`로 이동했습니다

- `EXP-243` 이후 저장소는 raw generated clip 자체를 고치기보다, `template overlay`, `hybrid source gate`, `manual review queue`, `approved inventory`, `lane hint`, `web consumption`으로 많이 전개됐습니다.
- 이 흐름은 실용적이고 현재 자원에서도 구현 가능한 방향입니다.
- 다만 이것은 `사진 몇 장 -> 자동 광고용 숏폼 생성`을 직접 닫은 것이 아니라, `승인된 소스 클립 + 패키징 + 보조 운영`으로 우회한 것입니다.

### 4.4 제품 플로우는 살아 있지만 출시 표면은 아직 연구 콘솔에 가깝습니다

- `services/api`와 `services/worker` 기준으로는 프로젝트 생성, 자산 업로드, generation background task, 결과 조회, publish, upload assist까지 제품 루프가 이어집니다.
- 그러나 web 기본 경로는 여전히 `local demo API`와 `demo-store` 의존이 강하고, `Renderer Pivot Lab`, prompt/copy/scene-plan 진단 정보가 메인 surface에 많이 노출됩니다.
- 따라서 현재 상태는 `제품이 전혀 없는 연구 저장소`는 아니지만, `바로 출시할 메인 UX로 정리된 상태`도 아닙니다.

### 4.5 현재 실제 자원과 가정상의 이상적 자원은 다릅니다

#### 현재 실제로 확인된 자원

- 저장소 내부 기록상 현재 실사용 가능한 상용 비디오 경로는 `OpenAI key 기반 Sora lane`뿐입니다.
- Veo는 내부 기록에서 `429 quota`가 있었고, Seedance는 이 저장소 기준 활성 실험선에 연결돼 있지 않습니다.
- 현재 저장소가 실제로 가진 강점은 `deterministic template renderer`, `hybrid packaging`, `approved hybrid source inventory`, `upload assist`입니다.

#### 가정상의 이상적 자원

- 상위 모델 API 접근, 안정적인 quota, 반복 실행 예산, 더 큰 리뷰 인력/시간, 더 넓은 approved candidate pool이 있으면 다른 결론이 가능할 수 있습니다.
- 그러나 그 경우에도 `원본 보존`, `repeatability`, `광고 문법 일관성`, `텍스트/브랜드 안전성` 문제는 별도로 남습니다.

### 4.6 외부 공식 문서로 다시 확인한 최신 사실

#### OpenAI / Sora

- `sora-2`, `sora-2-pro`는 OpenAI API 문서에 공식 등재돼 있고, `v1/videos` 엔드포인트가 안내돼 있습니다.
- 가격은 공식 문서 기준 `Sora 2 = $0.10/sec`, `Sora 2 Pro = $0.30/sec`입니다.
- rate limit은 usage tier에 따라 다르며, 공식 모델 문서에는 `Free not supported`, `Tier 1 25 RPM`, `Tier 5 375 RPM`이 표기돼 있습니다.

#### Google / Veo

- Gemini API 가격 문서는 `Veo 3.1`이 `paid tier only`라고 명시합니다.
- 공식 가격은 Gemini API 기준 `Veo 3.1 Standard with audio = $0.40/sec`, `Fast = $0.10~0.30/sec`, `Lite = $0.05~0.08/sec`입니다.
- Vertex AI 문서 기준 `veo-3.1-fast-generate-001` GA는 지역별 분당 50 request quota가 보이지만, `veo-3.1-generate-preview`는 10 RPM으로 더 빡빡합니다.
- 즉 Veo는 분명 강력한 상용 옵션이지만, 무료나 가벼운 시험선이 아니라 `유료/쿼터 관리형 자원`입니다.

#### Seedance

- ByteDance / BytePlus 공식 문서 기준으로 `Seedance 2.0` 관련 소개, API 호환 문서, 가격 문서가 존재합니다.
- BytePlus 가격 문서는 `dreamina-seedance-2-0-260128`와 `fast`의 토큰 단가 및 예시 비용을 공개합니다.
- 다만 이 저장소의 현재 자원 상태에는 Seedance key/credit/runtime 연결이 포함돼 있지 않으므로, 이번 판정에서 Seedance는 `공식 접근 경로는 있으나 현재 우리가 실제로 가진 자원은 아닌 상태`로 분류했습니다.

## 5. 판정

### 5.1 현재 진행방향 총평

- 판정: `부분적으로 맞지만, 핵심은 현재 비전 그대로 닫히지 않았고 최근에는 hybrid 운영화 쪽으로 드리프트가 생겼습니다.`
- 맞는 부분:
  - 본선 template/packaging baseline을 계속 다듬은 흐름
  - 업로드/결과/게시 보조까지 서비스 루프를 유지한 점
  - raw clip과 광고 패키징 문제를 분리해 본 점
- 틀어진 부분:
  - `광고 숏폼 생성`의 핵심 baseline이 닫히지 않은 상태에서, 승인/선정/인벤토리/힌트 같은 운영 레이어가 점점 두꺼워졌습니다.
  - 이 흐름을 제품 정의 변화로 인정하지 않으면, 현재 상태는 baseline 축적이라기보다 `baseline 미확정 상태의 우회적 드리프트`에 가깝습니다.

### 5.2 A. 현재 비전 그대로의 출시 가능성

- 판정: `현재 자원 기준 사실상 어렵습니다.`
- 이유:
  1. 핵심 약속은 `사진 몇 장 -> 광고용 숏폼 영상`인데, raw generation baseline이 아직 일관되게 닫히지 않았습니다.
  2. 현재 저장소가 실제로 잘하는 것은 `광고 패키징`이지, `고품질 생성형 숏폼 자동 생성`이 아닙니다.
  3. 내부 기록상 Sora는 일관된 production baseline이 아니었고, Veo는 upper-bound reference일 뿐 product-safe baseline이 아니었습니다.

### 5.3 B. scope를 줄인 경우의 출시 가능성

- 판정: `조건부가 아니라 현실적으로 가능합니다.`
- 전제:
  - 제품 정의를 `완전 자동 숏폼 생성 서비스`에서 `광고 패키징/보조 제작 도구`로 낮춰야 합니다.
  - 본선은 `product_control_motion + approved hybrid source + template overlay + upload assist`가 됩니다.
- 이 경우 가능한 약속:
  - 사진 업로드
  - 템플릿 기반 광고 결과물 생성
  - 필요 시 승인된 hybrid source clip 적용
  - 캡션/게시글/업로드 보조까지 묶은 실무 도구

### 5.4 C. 현재 자원 조건에서 가능한가

- 판정: `원형 비전은 어렵고, 축소 비전은 가능합니다.`
- 현재 실제 자원으로 가능한 것:
  - deterministic/hybrid 기반 광고 패키징
  - 내부 승인 inventory를 활용한 제한적 hybrid generation
  - 업로드 보조 및 결과 패키지 제공
- 현재 실제 자원으로 어려운 것:
  - 상위 생성 모델 품질을 전제로 한 fully automatic shortform generation
  - 반복 안정성과 원본 보존까지 만족하는 high-motion video baseline

### 5.5 D. 상위 모델 접근이 열린다고 가정하면 가능한가

- 판정: `조건부 가능`입니다.
- 단, 여기서 `가능`은 `품질 상한을 올릴 수 있다`는 뜻이지, `문제가 자동으로 해결된다`는 뜻은 아닙니다.
- 남는 리스크:
  1. 원본 제품/음식/텍스트/QR 보존
  2. repeatability
  3. 비용과 quota
  4. human review 필요성
  5. 생성 결과를 광고 문법과 브랜드 안전성 기준으로 묶는 문제

## 6. 지금까지의 실험 축 정리

### 6.1 진짜 남는 실험

- prompt/copy baseline freeze
- product_control_motion uplift
- shot-aware renderer baseline
- hybrid packaging proof -> renderer bridge -> generation path 연결
- approved hybrid inventory와 API/web consume path

### 6.2 필요했지만 이제 닫아야 할 실험

- 같은 질문을 반복하는 Sora phrase-level OVAAT
- single-photo crop 미세조정 반복
- edit path를 같은 조건으로 계속 재시도하는 축
- copy baseline gap을 연구처럼 계속 확장하는 작업

### 6.3 방향이 샌 실험

- 핵심 생성 baseline이 안 닫힌 상태에서 계속 불어나는 manual review / approved inventory / lane hint 운영 확장
- 이유:
  - 이 축 자체는 유용하지만, 원래 제품 약속을 유지한 채 본선처럼 키우면 `광고 생성 서비스`가 아니라 `큐레이션된 패키징 운영 시스템`으로 제품이 바뀝니다.

## 7. 지금 기준의 baseline 정리

### 7.1 product / service baseline

- 현재 baseline: `template result package + upload assist`
- 판정: `진짜 baseline입니다`

### 7.2 prompt / model baseline

- 현재 baseline: copy 쪽은 사실상 freeze
- 판정: `진짜 baseline입니다`

### 7.3 local / open-source video baseline

- 현재 baseline: `보존은 되지만 motion 설득력이 약한 near-static`
- 판정: `진짜 production baseline은 아닙니다`

### 7.4 paid frontier model baseline

- 현재 baseline: `upper-bound reference 또는 제한적 hybrid source 후보`
- 판정: `아직 production baseline이라고 부르기 어렵습니다`

## 8. 지금 기준의 우선순위

### 1순위: 제품 정의를 먼저 닫기

- `완전 생성형 광고 숏폼 서비스`를 계속 주장할지,
- 아니면 `hybrid 광고 패키징/보조 도구`로 제품 정의를 수정할지 먼저 결정해야 합니다.
- 이 판단 없이 실험을 더 해도 다시 드리프트가 납니다.

### 2순위: 모델 접근 전략 재정의

- 현재 자원으로 본선이 가능한지 아닌지 이미 대부분 드러났기 때문에, 다음 질문은 `무엇을 더 실험할까`가 아니라 `상위 모델 접근을 예산/정책/계약으로 확보할 것인가`입니다.
- 확보하지 못하면 현재 제품 정의를 축소해야 합니다.

### 3순위: 제품 구현 복귀

- scope를 축소한다면, 이제는 실험 UI와 진단 surface를 뒤로 보내고 `실제 사용자 메인 플로우`를 정리해야 합니다.
- 즉 다음 구현 우선순위는 새 prompt가 아니라 `launch surface 정리`입니다.

## 9. 계속 / 중단 / 보류

### 9.1 계속할 것

- template/hybrid packaging 본선 정리
- approved hybrid source를 활용한 제한적 생성 경로
- upload assist / result package / publish 연결
- 최소한의 quality gate와 review 기준 유지

### 9.2 지금 바로 멈출 것

- single-photo Sora prompt/crop/edit 미세 반복
- raw generation baseline이 안 닫힌 상태에서의 운영 레이어 확장
- `상위 모델만 붙이면 해결된다`는 가정 아래의 낙관적 실험 분산

### 9.3 판단 보류할 것

- Veo/Seedance를 본선 채택할지 여부
- 이유:
  - 공식 접근 경로는 확인됐지만, 현재 저장소의 실제 자원/예산/쿼터/운영 조건에는 아직 포함돼 있지 않습니다.
  - 접근이 열린 뒤에도 preserve/repeatability 검증이 추가로 필요합니다.

## 10. 결론

- 냉정하게 말하면, 현재 자원으로는 `사진 몇 장을 넣으면 광고용 숏폼 영상을 바로 생성해 주는 서비스`를 원형 그대로 출시하기 어렵습니다.
- 반면 `광고 패키징/보조 제작 도구`로 정의를 낮추면, 이 저장소는 이미 출시 가능한 본선을 상당 부분 갖고 있습니다.
- 따라서 다음 세션의 정답은 `새 실험 확대`가 아니라 아래 둘 중 하나입니다.
  1. 상위 모델 접근 전략을 사업/예산 문제로 올려서 다시 가져오거나
  2. 제품 정의를 hybrid packaging 중심으로 공식 축소하고 구현 복귀하기

## 11. 검증

- 새 생성 실험은 수행하지 않았습니다.
- 대신 아래를 통해 현재 상태를 다시 검증했습니다.
  - `uv run --project services/worker pytest services/worker/tests -q`
  - `uv run --project services/api pytest services/api/tests -q`
  - `npm run build:web`
  - 내부 문서/코드 전수 재검토
  - OpenAI / Google / BytePlus 공식 문서 확인

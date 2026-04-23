# 팀원별 기여 정리

이 문서는 발표나 인수인계에서 "누가 어떤 축을 맡았고, 그중 지금 저장소에 무엇이 남아 있는가"를 설명하기 위한 정리 문서입니다.

메인 [README.md](../README.md)는 프로젝트 소개 문서로 두고, 이 문서는 그보다 한 단계 안쪽의 기록으로 사용합니다.

## 먼저 정리할 점

- `팀원들 구현/` 폴더는 **통합 전 보관본**입니다.
- 이 폴더는 GitHub에 올릴 기준선이 아니므로, 이 문서의 근거 경로에는 넣지 않았습니다.
- 아래에 적은 경로는 모두 **현재 trunk 안에 실제로 남아 있는 파일**만 사용했습니다.

즉, 이 문서는 "예전에 각자 이런 폴더가 있었다"가 아니라, "그 작업 중 무엇이 지금 저장소에 반영되었는가"를 기준으로 읽으시면 됩니다.

## 지금 저장소 기준 요약

이 프로젝트는 한 사람이 처음부터 끝까지 만든 저장소가 아니라, 팀원별 강점을 하나의 trunk로 정리한 결과물입니다.

- 임창현: 기준 문서 작성/배포, trunk 기준선 설계, 선택 통합 리드, 실제 동작 검증, 발표용 문서와 자산 정리
- 신유철: 모델 실험 축과 Wan2.1-VACE 연구 근거
- 이진석: 모바일 앱형 화면 톤, 인증/보안 강화, 채널 연동 UX 개선
- 최무영: 로그인/인증/API 기본 흐름
- 서유종: worker 구조 경계와 UX 프로토타입 흐름

아래에는 이 다섯 축이 현재 저장소에서 어디에 남아 있는지 정리했습니다.

## 임창현

임창현 작업은 크게 세 갈래입니다. 첫째는 팀이 같은 목표와 경계를 공유하도록 기준 문서를 먼저 고정한 일, 둘째는 trunk를 실제로 돌아가는 기준선으로 묶는 통합 리드 역할, 셋째는 어떤 방향을 채택하고 어떤 방향을 보류할지 판단하는 실험 기록입니다.

현재 저장소에 바로 남아 있는 근거는 아래입니다.

- [docs/planning/01_SERVICE_PROJECT_PLAN.md](../docs/planning/01_SERVICE_PROJECT_PLAN.md)
- [docs/planning/02_USER_FLOW_AND_SCREEN_POLICY.md](../docs/planning/02_USER_FLOW_AND_SCREEN_POLICY.md)
- [docs/planning/03_CONTENT_PIPELINE_AND_TEMPLATE_SPEC.md](../docs/planning/03_CONTENT_PIPELINE_AND_TEMPLATE_SPEC.md)
- [docs/planning/04_API_CONTRACT.md](../docs/planning/04_API_CONTRACT.md)
- [docs/planning/05_DATA_ARCHITECTURE_AND_REPO_STRUCTURE.md](../docs/planning/05_DATA_ARCHITECTURE_AND_REPO_STRUCTURE.md)
- [docs/planning/06_EVALUATION_TEST_AND_OPERATIONS.md](../docs/planning/06_EVALUATION_TEST_AND_OPERATIONS.md)
- [docs/daily/2026-04-23-codex.md](../docs/daily/2026-04-23-codex.md)
- [docs/testing/test-scenario-186-root-selective-integration-freeze.md](../docs/testing/test-scenario-186-root-selective-integration-freeze.md)
- [docs/presentation/assets/app](../docs/presentation/assets/app)
- [scripts/dev-api.mjs](../scripts/dev-api.mjs)

이 여섯 개 planning 문서는 제품 범위, 화면 정책, 생성 파이프라인, API 계약, 데이터 구조, 평가/운영 기준을 팀 공통 기준으로 먼저 고정한 문서입니다. 실제 협업은 이 문서를 먼저 배포한 뒤, 팀원별 구현을 그 기준에 맞춰 나누는 방식으로 시작했습니다.

또 하나 중요한 축이 [docs/experiments](../docs/experiments)입니다. 이 경로에는 prompt/copy 실험, B급 레이아웃 실험, scene preview 구조, hybrid source selection, manual review 흐름 같은 방향 검토가 남아 있습니다.

대표적으로는 아래 문서들이 있습니다.

- [EXP-01-prompt-harness-and-slot-guidance.md](../docs/experiments/EXP-01-prompt-harness-and-slot-guidance.md)
- [EXP-03-b-grade-video-layout.md](../docs/experiments/EXP-03-b-grade-video-layout.md)
- [EXP-97-self-serve-ai-ad-platform-patterns.md](../docs/experiments/EXP-97-self-serve-ai-ad-platform-patterns.md)
- [EXP-225-video-baseline-reset-after-copy-freeze.md](../docs/experiments/EXP-225-video-baseline-reset-after-copy-freeze.md)

이 기록은 신유철 모델 레인처럼 "최종 채택된 모델 구현"을 의미하지는 않습니다. 대신 프로젝트가 어떤 방향을 실제로 검토했고, 왜 지금 구조를 택했는지 설명해 주는 근거입니다.

## 신유철

신유철 작업은 이 프로젝트의 모델 실험 축입니다. trunk 기준으로 보면, "앱에 바로 붙은 최종 런타임"이라기보다 "실험 저장소를 보존하고 worker 연동 경계를 잡아 둔 상태"라고 보는 것이 정확합니다.

현재 저장소에 남아 있는 대표 근거는 아래입니다.

- [external/i2v-motion-experiments](../external/i2v-motion-experiments)
- [external/i2v-motion-experiments/TRUNK_SNAPSHOT.md](../external/i2v-motion-experiments/TRUNK_SNAPSHOT.md)
- [services/worker/adapters/adapter_wan2_vace.py](../services/worker/adapters/adapter_wan2_vace.py)
- [testing/shin-vm-origin-verification-and-backup.md](testing/shin-vm-origin-verification-and-backup.md)
- [docs/presentation/assets/model](../docs/presentation/assets/model)
- [docs/daily/2026-04-23-codex.md](../docs/daily/2026-04-23-codex.md)

이 축에서 설명할 수 있는 것은 분명합니다.

- Wan2.1-VACE 실험 워크스페이스를 trunk 안에 보존했다.
- worker에서 그 실험 저장소를 호출할 수 있는 경계를 만들었다.
- 발표용으로 실제 실험 샘플과 화면 캡처를 남겼다.
- 2026-04-23 기준으로 VM 원본 레포 커밋과 trunk 스냅샷이 같은 값(`6ea9ffc`)인지 직접 확인했다.

반대로 아직 조심해서 말해야 하는 부분도 분명합니다.

- 현재 앱의 실제 생성 경로는 trunk 내부 렌더러 기준입니다.
- 신유철 실험은 근거와 스냅샷은 정리됐지만, 앱 런타임에 직접 붙어 있다고 말하면 안 됩니다.

## 이진석

이진석 작업은 디자인과 사용자 흐름만이 아니라, 보안과 인증 강화 쪽에서도 비중이 있습니다. 원본 Vite 앱 전체를 trunk에 넣은 것은 아니지만, 현재 `apps/web`에 남아 있는 모바일 앱형 톤과 흐름, 그리고 `main`에 반영된 인증/보안 강화에는 이진석 작업이 직접 연결됩니다.

현재 저장소에서 확인 가능한 대표 근거는 아래입니다.

- [apps/web/src/components/simple-workbench.tsx](../apps/web/src/components/simple-workbench.tsx)
- [apps/web/src/components/app-nav.tsx](../apps/web/src/components/app-nav.tsx)
- [apps/web/src/app/login/page.tsx](../apps/web/src/app/login/page.tsx)
- [apps/web/src/app/account/page.tsx](../apps/web/src/app/account/page.tsx)
- [apps/web/src/components/account-center.tsx](../apps/web/src/components/account-center.tsx)
- [apps/web/src/app/globals.css](../apps/web/src/app/globals.css)
- [apps/web/src/middleware.ts](../apps/web/src/middleware.ts)
- [services/api/app/main.py](../services/api/app/main.py)
- [services/api/app/core/rate_limit.py](../services/api/app/core/rate_limit.py)
- [services/api/app/services/crypto.py](../services/api/app/services/crypto.py)
- [docs/daily/2026-04-23-codex.md](../docs/daily/2026-04-23-codex.md)

발표에서는 이렇게 설명하시면 자연스럽습니다.

- 원본 앱 전체를 가져온 것은 아니다.
- 다만 메인 화면, 로그인 화면, 하단 탭 구조처럼 사용자가 처음 만나는 톤은 이진석이 잡아 둔 방향을 기준으로 정리했다.
- 동시에 쿠키 인증, CSRF, rate limit, OAuth 토큰 암호화, 토큰 만료 UX 같은 보안 강화도 이진석 브랜치에서 들어와 현재 trunk에 반영됐다.
- 즉 이 축은 "디자인만 담당"이 아니라, **사용자-facing 화면과 보안 강화를 같이 밀어 올린 작업**으로 보는 편이 맞다.

## 최무영

최무영 작업은 로그인/인증/API 뼈대 쪽에서 의미가 큽니다. 특히 현재 trunk에서 회원가입, 로그인, 세션, `me`, 프로젝트 생성 같은 흐름이 돌아가도록 정리된 부분과 맞닿아 있습니다.

현재 저장소에서 확인 가능한 대표 근거는 아래입니다.

- [services/api/app/api/routes.py](../services/api/app/api/routes.py)
- [services/api/app/core/security.py](../services/api/app/core/security.py)
- [packages/contracts/schemas/auth.ts](../packages/contracts/schemas/auth.ts)
- [docs/testing/test-scenario-186-root-selective-integration-freeze.md](../docs/testing/test-scenario-186-root-selective-integration-freeze.md)

이 축은 "최종 운영 구조 확정"이라기보다, 실제 로그인/인증/API 기본선을 trunk에 남긴 작업으로 보는 편이 맞습니다.

정리하면:

- auth/API 기본 골격은 현재 저장소에 남아 있습니다.
- 하지만 queue 구조나 운영 인프라 비교안까지 최종 확정됐다고 말하면 안 됩니다.

## 서유종

서유종 작업은 두 가지로 남아 있습니다. 하나는 worker 구조의 경계를 더 분명하게 보는 시각이고, 다른 하나는 UX 플로우를 독립 프로토타입으로 빠르게 보여 줄 수 있게 만든 부분입니다.

현재 저장소에서 확인 가능한 대표 근거는 아래입니다.

- [services/worker/README.md](../services/worker/README.md)
- [prototypes/README.md](prototypes/README.md)
- [prototypes/web-flow-prototype.html](prototypes/web-flow-prototype.html)
- [docs/daily/2026-04-23-codex.md](../docs/daily/2026-04-23-codex.md)

현재 `services/worker`의 `adapters / pipelines / renderers` 경계 정리는 서유종이 잡아 둔 방향과 닿아 있습니다. UX 쪽은 [web-flow-prototype.html](prototypes/web-flow-prototype.html)로 별도 보존했고, 실제 `apps/web`에는 흐름 참고 수준으로만 반영했습니다.

즉, 이 축은 "프로토타입이 그대로 제품이 되었다"가 아니라, "프로토타입이 trunk 구조와 사용자 흐름 정리에 영향을 줬다"로 설명하는 것이 맞습니다.

## 발표에서 이 문서를 쓰는 방법

이 문서는 팀원별 소개를 길게 늘어놓기 위한 문서가 아닙니다. 발표에서는 아래 정도로만 쓰시면 충분합니다.

1. 메인 README에서 프로젝트 전체를 설명합니다.
2. 팀원별 역할이나 근거를 물으면 이 문서로 내려옵니다.
3. 설명할 때는 항상 "누가 무엇을 했다"와 "그중 지금 저장소에 무엇이 남아 있는가"를 같이 말합니다.

## 마지막으로

이 문서에서 일부러 빼 둔 것도 있습니다.

- 통합 전 개인 작업 폴더
- GitHub에 올리지 않은 비교 자료
- 로컬에서만 잠깐 썼던 중간 산출물

그 자료들은 통합 과정의 참고 자료로는 의미가 있었지만, 공개 trunk의 근거 문서에는 맞지 않습니다. 발표나 포트폴리오에서는 지금 저장소에 남아 있는 기준선만으로도 충분히 설명 가능해야 합니다.

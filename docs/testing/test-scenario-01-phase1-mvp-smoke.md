# Test Scenario 01 - Phase 1 MVP Smoke

- 날짜: 2026-04-07
- 목적: Phase 1 Must 범위의 로컬 데모 동작 여부를 빠르게 검증
- 기준 문서:
  - `docs/planning/04_API_CONTRACT.md`
  - `docs/planning/06_EVALUATION_TEST_AND_OPERATIONS.md`

## 시나리오

### TS-01 카페 신메뉴 생성

- 업종: `cafe`
- 목적: `new_menu`
- 스타일: `friendly`
- 지역: `성수동`
- 채널: `instagram`
- 입력 이미지: 2장

### 검증 항목

1. 프로젝트 생성이 가능해야 합니다.
2. 자산 업로드 시 경고 taxonomy가 반환되어야 합니다.
3. generate 요청 후 status polling이 `queued -> preprocessing -> generating -> generated`로 진행되어야 합니다.
4. result 응답에 `video`, `post`, `copySet`이 포함되어야 합니다.
5. publish auto 또는 assist fallback 중 하나가 시연 가능해야 합니다.
6. quick action 기반 regenerate가 새 generation run으로 생성되어야 합니다.

## 실행 기록

### 실행 명령

1. `npm run api:test`
2. `npm run worker:test`
3. `npm run lint:web`
4. `npm run build:web`
5. `npm run check`

### 실제 확인한 내용

1. API smoke test에서 프로젝트 생성, 자산 업로드, generate, status polling, result 조회, publish 흐름을 검증했습니다.
2. Worker test에서 preprocess, template resolve, copy generation, FFmpeg 기반 render, publish fallback 기록까지 검증했습니다.
3. Web lint/build에서 생성 마법사, 상태 polling, quick action, 업로드 보조 플로우를 포함한 Next.js 앱 정적 빌드를 검증했습니다.
4. 초기 검증 중 `apps/web` 타입 정합성 문제와 Next.js 동적 route handler 타입 제약이 발견되어 수정 후 재검증했습니다.

## 결과 요약

1. `npm run check` 기준 전체 통과했습니다.
2. Phase 1 Must 핵심 데모 경로는 로컬 환경에서 재현 가능합니다.
3. `instagram`은 자동 게시 시뮬레이션, `youtube_shorts`/`tiktok`은 assist fallback 중심으로 동작합니다.
4. `packages/contracts`와 `packages/template-spec` 기준의 상태값/quick action/template 메타데이터가 API, worker, web에 연결되었습니다.

## 실패/제약

1. 외부 SNS 실제 연동은 아직 시뮬레이션 단계입니다. 발표용 데모 기준으로는 충분하지만 운영 연동 검증은 별도 작업이 필요합니다.
2. 현재 로컬 런타임은 ADR-001 기준으로 SQLite + 로컬 파일시스템을 사용합니다. 기획 문서의 PostgreSQL/Redis/Object Storage와는 차이가 있습니다.
3. auth/store/social-account 일부 흐름은 로컬 데모 재현성을 위해 demo user/state를 기본값으로 사용합니다.
4. web 복원 편의를 위해 `GET /api/projects/{projectId}/assets` 확장 endpoint를 함께 사용합니다. canonical 본문은 `GET /api/projects/{projectId}`에 유지했습니다.

## 다음 액션

1. `Gemma 4`를 포함한 실제 모델 비교 실험은 `docs/experiments/`에 벤치마크 형식으로 추가해야 합니다.
2. 외부 publish adapter와 OAuth 연동은 assist fallback을 유지한 채 단계적으로 실서비스 연동으로 대체해야 합니다.
3. Phase 2 진입 전 PostgreSQL/Redis/S3 계층 전환 계획을 별도 ADR 또는 migration 문서로 구체화해야 합니다.

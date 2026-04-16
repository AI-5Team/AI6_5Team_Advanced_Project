# 2026-04-16 Selective Integration

## 목적

- 루트 저장소를 trunk로 고정한 상태에서 기능 선별 통합 계획을 실제 코드와 문서에 반영합니다.
- 발표 전 재분배 기준이 되는 최소 통합선(auth UI, worker adapter 경계, freeze 문서)을 먼저 확정합니다.

## 수행 내용

### 1. planning/adr/testing 기준선 추가

- `docs/planning/10_ROOT_TRUNK_SELECTIVE_INTEGRATION_PLAN.md`
- `docs/adr/ADR-010-root-trunk-selective-integration.md`
- `docs/testing/test-scenario-186-root-selective-integration-freeze.md`

위 문서들에 다음을 기록했습니다.

- trunk 기준선
- 팀원별 채택/보류 기준
- freeze 전 시나리오
- 남은 리스크

### 2. 웹 인증 게이트 연결

- `apps/web` 루트 레이아웃에 auth gate를 추가했습니다.
- 로그인/회원가입/세션 저장/`me` 검증을 현재 auth 계약에 연결했습니다.
- 인증 전에는 보호 화면을 직접 열지 못하도록 했고, 인증 후에는 기존 `만들기 / 이력 / 채널` 화면을 그대로 사용합니다.

### 3. API auth 동작 정합화

- demo 계정이 로그인 가능하도록 login 경로에서 demo state 보장을 추가했습니다.
- `/api/me`는 Bearer token이 없거나 위조된 경우 `401 AUTH_REQUIRED`를 반환하도록 정리했습니다.
- register/login/me에 대한 smoke test를 추가했습니다.

### 4. worker Wan2.1-VACE adapter 경계 추가

- worker가 실험 저장소를 직접 import하지 않도록 subprocess 기반 adapter 경계를 추가했습니다.
- workspace/script/python/timeout/default args를 환경변수로 주입받도록 구성했습니다.
- command build 및 subprocess smoke run을 unit test로 검증했습니다.

### 5. API DB 기준선 정리

- `services/api/app/core/bootstrap.py`와 `services/api/app/models/entities.py`는 현재 trunk 기준과 맞지 않는 SQLAlchemy 초안으로 판단해 제거했습니다.
- freeze 기준 DB access는 `services/api/app/core/database.py`의 raw sqlite3 경로로 고정했습니다.
- `services/api/app/repos/README.md`, `services/api/app/models/README.md`를 추가해 현재 미사용/보류 상태를 명시했습니다.

## 결과 판단

1. trunk 기준 통합 방향이 문서로 고정됐습니다.
2. 로그인 흐름은 기존 auth API와 실제 UI를 통해 동작하게 됐습니다.
3. 모델 실험 저장소는 제품 런타임과 직접 결합하지 않고 adapter 경계로만 연결되도록 정리됐습니다.
4. API DB 기준선은 raw sqlite3로 명확히 고정됐습니다.

## 남은 리스크

1. 프로젝트/채널/프로필 데이터는 아직 demo-state 기준이라 사용자별 격리가 남아 있습니다.
2. Redis/RQ 비교 결과는 아직 trunk 채택으로 확정되지 않았습니다.
3. Wan2.1-VACE 실제 GPU lane smoke run은 외부 workspace 준비 후 추가 기록이 필요합니다.

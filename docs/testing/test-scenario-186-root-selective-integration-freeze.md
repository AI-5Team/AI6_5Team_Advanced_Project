# Test Scenario 186: 루트 기준 기능 선별 통합 freeze 검증

## 목적

- 루트 trunk 기준 통합본이 freeze 전 최소 기능/보안 시나리오를 통과하는지 확인합니다.
- 인증 UI 연결, 기존 생성 파이프라인, worker adapter 경계가 동시에 깨지지 않는지 확인합니다.

## 범위

1. 인증
2. 프로젝트 생성/업로드/생성/결과
3. 게시 fallback
4. 채널 연동 상태 반영
5. worker Wan2.1-VACE adapter 경계

## 사전 조건

- `apps/web`는 trunk 기준 화면을 사용합니다.
- API는 `/api/auth/register`, `/api/auth/login`, `/api/me`를 제공합니다.
- worker는 `services/worker/adapters/adapter_wan2_vace.py` 경계를 통해 외부 실험 저장소를 호출할 수 있습니다.

## 테스트 항목

### 기능 시나리오

1. 회원가입 → 로그인 → `GET /api/me`
2. 프로젝트 생성 → 자산 업로드 → 생성 → 결과 조회
3. 결과 확인 → `publishMode=assist` 또는 auto fallback
4. 계정 연동 시작 → callback → 상태 반영
5. 이력 화면 진입 → 기존 프로젝트 재열기
6. worker Wan adapter command build 및 smoke run

### 보안 시나리오

1. 잘못된 비밀번호로 로그인 시 `401 INVALID_CREDENTIALS`
2. 위조 토큰으로 `GET /api/me` 호출 시 `401 AUTH_REQUIRED`
3. 미연동 채널 auto publish 시 `assist_required`
4. 지원하지 않는 채널 요청 시 `400 UNSUPPORTED_CHANNEL`
5. 잘못된 파일 형식/크기 제한 위반은 기존 업로드 검증 시나리오로 연계

## 이번 반영 기준 결과

| 항목 | 결과 | 근거 |
|---|---|---|
| 회원가입/로그인/`me` | 통과 | API smoke auth test 추가 |
| 잘못된 비밀번호/위조 토큰 | 통과 | API smoke auth test 추가 |
| trunk auth UI 연결 | 통과 | `apps/web` auth gate 추가 |
| worker Wan adapter 경계 | 통과 | worker adapter unit test 추가 |
| 프로젝트/업로드 작업 사용자 소유권 경계 | 통과 | API ownership scope test 추가 |
| demo seed/state 제거 | 보류 | 현재 demo-state 기반 흐름 일부 유지 |

## 남은 리스크

1. 프로젝트/업로드 작업 소유권 검증은 보강했지만, 일부 데모 seed/state는 발표 안정성을 위해 남아 있습니다.
2. Wan adapter는 환경변수와 외부 workspace가 준비된 경우에만 실제 lane을 실행할 수 있습니다.
3. freeze 전 Redis/RQ 비교 결과를 추가 기록해야 합니다.

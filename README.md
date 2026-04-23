# AI6_5Team_Advanced_Project

이 저장소는 **팀 최종 trunk**이자, 팀원 작업물을 선별 통합한 뒤 다시 업무를 재분배하기 위한 **기준선 저장소**입니다.

현재 상태는 다음 두 가지 성격을 함께 가집니다.

1. **통합 기준선**
   - `services/api/app`
   - `apps/web`
   - `packages/contracts`
   - `docs/planning`
2. **가이드 구현 상태**
   - 팀원 작업물을 어떻게 trunk에 흡수할지 보여주는 예시 구현이 일부 반영되어 있습니다.
   - 따라서 지금 코드는 “최종 확정본”이라기보다, **이 방향으로 통합한다는 기준과 샘플**로 보시면 됩니다.

---

## 1. 현재 trunk 원칙

- 기준선은 **현재 루트 저장소**입니다.
- 통합은 **폴더 통째 병합이 아니라 기능 단위 선별 이식**으로 진행합니다.
- 프로덕션 웹 앱은 **`apps/web` 하나만 유지**합니다.
- 공용 타입과 계약의 source of truth는 **`packages/contracts` + `docs/planning`**입니다.
- 실험 저장소는 제품 런타임을 직접 대체하지 않고, 필요한 경우 **메인 레포 안 스냅샷 + adapter 경계**로 연결합니다.

---

## 2. 지금 반영된 가이드성 구현

현재 trunk에는 아래 항목이 **가이드 격으로 이미 반영**되어 있습니다.

### Web

- `apps/web`를 메인 웹 앱으로 유지
- `register/login/me` 계약을 기준으로 한 auth gate 연결
- 기존 만들기 / 이력 / 채널 화면을 보호 화면으로 유지

### API

- `services/api/app` 구조 유지
- DB access는 현재 raw `sqlite3` 기준선 유지
- `/api/auth/register`, `/api/auth/login`, `/api/me` 기준 인증 흐름 정리
- `me`는 Bearer token이 없거나 위조된 경우 `401 AUTH_REQUIRED`

### Worker

- `services/worker/adapters`, `pipelines`, `renderers` 구조 유지
- `Wan2.1-VACE`는 실험 저장소를 직접 import하지 않고
  `adapter_wan2_vace` 경계를 통해 subprocess 기반으로 연결
- 신유철 실험 저장소는 `external/i2v-motion-experiments`에 **코드 스냅샷**으로 보존

이 구현들은 지금 당장 완전한 업무 완료물이라기보다,
**팀원별 후속 작업이 어디에 붙어야 하는지 보여주는 trunk 기준선**입니다.

---

## 3. 팀원 작업물 통합 기준

| 대상 | trunk 반영 원칙 |
|---|---|
| 루트 저장소 | source of truth 유지 |
| 신유철 작업물 | GitHub 실험 저장소를 `external/i2v-motion-experiments`에 코드 스냅샷으로 보존하고, trunk 런타임은 worker adapter 경계로만 연결 |
| 이진석 작업물 | Vite 앱 전체 채택이 아니라 화면 흐름/디자인 자산/상태 설계만 `apps/web`에 포팅 |
| 최무영 작업물 | Redis/RQ 큐 패턴은 비교 후 운영 이점이 확인될 때만 선택 채택 |
| 서유종 작업물 | worker 내부 `adapters / pipelines / renderers` 경계 개선에 적극 반영 |

### 외부 모델 실험 스냅샷

- 원본 저장소: `https://github.com/youuuchul/i2v-motion-experiments`
- trunk 반입 위치: `external/i2v-motion-experiments`
- 반입 기준 commit: `6ea9ffc060655b2eadf394e5b98e85dc89aaec8e`
- 반입 범위: 코드, config, docker, 문서, 테스트
- 제외 범위: `.git`, 모델 weight/cache, 개인 샘플 이미지, outputs/logs, Drive 산출물

이 스냅샷은 **발표/인수인계/재현 근거 보존용**입니다. 제품 웹/API가 이 경로를 직접 import 하지는 않고,
`services/worker/adapters/adapter_wan2_vace.py`가 `--config` 기반 subprocess 경계로만 호출합니다.

### 통합 시 금지

- 폴더 통째 복사
- `node_modules`, `.env`, 실행 로그, 산출 영상/이미지, 임시 업로드, 로컬 DB/캐시 반입
- `packages/contracts`를 거치지 않는 public contract 임의 변경

---

## 4. 업무 재분배 기준선

| 업무 | 주담당 | 범위 |
|---|---|---|
| 모델 개선 | 신유철 | 모델 선택, 실험, 추론 설정, benchmark, worker adapter 개선 |
| 보안 기능 | 이진석 | 업로드 검증, 외부 연동 권한 흐름, 토큰/채널 상태 UX, rate limit, 오류 처리 정책 |
| 로그인 + 관련 보안 | 최무영 | register/login/me 연결, 보호 라우트, 토큰 처리, 인증 예외 정리 |
| UI/UX 개선 | 서유종(구현) + 이진석(디자인 리뷰) | `apps/web` 단계형 화면 구조 정리 |
| 최종 종합 + 발표 | 임창현 | 통합 승인, freeze, 발표 기준선 확정 |

---

## 5. 디렉토리 가이드

```text
apps/web              Next.js 기반 메인 웹 앱
services/api/app      FastAPI API 기준 구현
services/worker       worker / adapter / pipeline 기준 구현
packages/contracts    공용 계약과 타입
external/i2v-motion-experiments  신유철 모델 실험 코드 스냅샷
docs/planning         canonical 기획 문서
docs/adr              주요 구조 의사결정 기록
docs/testing          freeze 전 테스트 시나리오
docs/daily            작업 기록
팀원들 구현           비교/선별 대상 작업물
```

### 실무 해석

- 새로운 UI 작업은 `apps/web` 기준으로 붙입니다.
- 새로운 API 계약은 먼저 `packages/contracts`와 `docs/planning`을 확인합니다.
- API DB 변경은 먼저 `services/api/app/core/database.py` 기준선과 planning 문서를 확인합니다.
- 모델 실험은 외부 실험 저장소 또는 별도 실험 경로에서 진행하고, trunk에는 adapter 경계만 반영합니다.

---

## 6. 실행 명령어

루트 기준 명령어입니다.

```bash
npm run api:test
npm run worker:test
npm run lint:web
npm run build:web
npm run check
```

웹 개발 서버:

```bash
npm run dev:web
```

---

## 7. 먼저 읽어야 할 문서

### planning

- `docs/planning/04_API_CONTRACT.md`
- `docs/planning/07_TEAM_RACI_AND_ROADMAP.md`
- `docs/planning/10_ROOT_TRUNK_SELECTIVE_INTEGRATION_PLAN.md`

### architecture

- `docs/adr/ADR-010-root-trunk-selective-integration.md`

### test / 기록

- `docs/testing/test-scenario-186-root-selective-integration-freeze.md`
- `docs/daily/2026-04-16-selective-integration.md`

---

## 8. 현재 남은 리스크

1. 인증 UI와 `me` 검증은 연결됐지만, 프로젝트/채널/프로필 데이터는 아직 demo-state 중심입니다.
2. `Wan2.1-VACE` 실험 스냅샷은 trunk 안에 보존됐지만, 실제 실행에는 별도 GPU 환경, HF 토큰, 샘플 자산이 필요합니다.
3. Redis/RQ 큐 패턴은 아직 비교 단계라 trunk 채택이 확정되지 않았습니다.
4. `repos/`는 아직 미사용이며, post-freeze에만 분리 대상으로 봅니다.

---

## 9. 운영 메모

- 지금 trunk는 “무조건 확정된 완성본”이 아니라 **통합 기준선 + 구현 가이드**입니다.
- 따라서 이후 팀원 작업은 trunk를 기준으로 이어가되, 중복 구현을 다시 들여오기보다 **현재 구조에 맞춰 흡수**하는 방식으로 진행해야 합니다.
- 연구/실험/비교 작업은 과정과 결과를 반드시 문서화해야 합니다.
- 외부 모델 실험은 `external/i2v-motion-experiments` 스냅샷을 기준으로 설명하고, VM 경로나 개인 계정 상태를 기준선으로 삼지 않습니다.

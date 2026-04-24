# docs 가이드

루트 [README.md](../README.md)는 프로젝트 소개와 포트폴리오 성격의 문서입니다.  
이 폴더는 그 뒤에서 받쳐 주는 **발표 / 검증 / 실험 / 인수인계용 참고 문서 모음**입니다.

## 먼저 볼 문서

### 발표 직전

1. [presentation/Project-report.md](presentation/Project-report.md)
2. [presentation/demo-checklist.md](presentation/demo-checklist.md)
3. [presentation/assets/README.md](presentation/assets/README.md)
4. [daily/2026-04-24-codex.md](daily/2026-04-24-codex.md)

### trunk 기준 이해

1. [planning/10_ROOT_TRUNK_SELECTIVE_INTEGRATION_PLAN.md](planning/10_ROOT_TRUNK_SELECTIVE_INTEGRATION_PLAN.md)
2. [adr/ADR-010-root-trunk-selective-integration.md](adr/ADR-010-root-trunk-selective-integration.md)
3. [daily/2026-04-16-selective-integration.md](daily/2026-04-16-selective-integration.md)

### 실행 / 검증 근거

1. [testing/README.md](testing/README.md)
2. [testing/test-scenario-186-root-selective-integration-freeze.md](testing/test-scenario-186-root-selective-integration-freeze.md)
3. [testing/shin-vm-origin-verification-and-backup.md](testing/shin-vm-origin-verification-and-backup.md)
4. [daily/2026-04-23-codex.md](daily/2026-04-23-codex.md)

### 팀원별 기록

1. [team-contributions-and-experiments.md](team-contributions-and-experiments.md)
2. [daily/2026-04-23-codex.md](daily/2026-04-23-codex.md)

## 폴더별 의미

### `planning/`

- 제품 방향
- API 계약
- 역할 분담
- trunk 통합 계획

실행 기준과 source of truth를 설명하는 문서들입니다.

### `adr/`

- 구조 결정
- 통합 원칙
- 구현 방향 변경 이유

왜 이런 구조로 갔는지를 설명합니다.

### `testing/`

- 시나리오별 테스트 문서
- freeze 전 검증 기준
- VM 원본 확인과 백업 기록

발표에서 “무엇을 확인했는가”를 말할 때 근거가 됩니다. 먼저 [testing/README.md](testing/README.md)에서 봐야 할 문서를 고른 뒤 세부 문서로 내려가면 됩니다.

### `daily/`

- 당일 작업 기록
- 검증 결과
- 통합/샘플/실험 반영 내역

가장 최신 상태는 [daily/2026-04-23-codex.md](daily/2026-04-23-codex.md)를 보시면 됩니다.
보고서/발표 준비를 다시 정리한 최신 작업은 [daily/2026-04-24-codex.md](daily/2026-04-24-codex.md)에도 남겨 두었습니다.

### `presentation/`

- 발표 대본 보조 문서
- 발표용 자산 묶음
- 프로젝트 보고서

슬라이드에 바로 넣을 이미지/영상은 [presentation/assets](presentation/assets) 아래에 있습니다.

### `archive/`

- 초기 기획 초안
- 이전 누적 이력
- 루트에서 내려 보낸 문서

현재 기준선 설명에는 직접 쓰이지 않지만, 맥락을 복원해야 할 때 참고하는 보관 구역입니다.

### `team-contributions-and-experiments.md`

- 팀원별 기여 근거
- 실험/프로토타입/스캐폴드 기록
- trunk 반영 여부 정리

### `experiments/`

- 실험 로그
- prompt / video / runtime 방향 검토

지금 발표용 설명에서는 전체를 다 볼 필요는 없고, 필요한 경우에만 근거로 인용하면 됩니다.

## 지금 문서로 바로 말할 수 있는 것

- trunk 통합 원칙
- 현재 앱에서 실제로 동작하는 흐름
- Shin VM 샘플 자산 반영 상태
- 실제 생성이 trunk 내부 가이드 렌더러 기준이라는 점
- 아직 남아 있는 리스크

## 발표 시 문서 사용 원칙

1. VM이나 개인 계정 상태보다 trunk 안 문서를 기준으로 말합니다.
2. “현재 되는 것”과 “아직 아닌 것”을 분리해서 설명합니다.
3. 실험 결과를 주장할 때는 `daily/`나 `testing/` 문서를 근거로 둡니다.

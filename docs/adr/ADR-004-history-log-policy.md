# ADR-004 누적 작업 히스토리는 `docs/archive/HISTORY.md`로 관리

- 상태: 승인
- 날짜: 2026-04-08

## 배경

현재 저장소에는 `docs/daily/`, `docs/testing/`, `docs/experiments/`, `docs/adr/`가 이미 있고, 실제 작업 내용은 이 경로들에 분산 기록되고 있습니다.  
다만 세션이 누적될수록 "지금까지 무엇이 완료됐고, 무엇이 남았는지"를 한 번에 파악하기 어렵습니다.

특히 이후 실험 세션은 별도 채팅에서 시작할 예정이므로, 새 세션이 바로 읽을 수 있는 누적 요약 파일이 필요합니다.

## 결정

1. 누적 히스토리 문서는 `docs/archive/HISTORY.md`에 둡니다.
2. 모든 작업 세션은 종료 전에 반드시 `docs/archive/HISTORY.md`를 갱신합니다.
3. `docs/archive/HISTORY.md`는 누적 요약 전용이며, 세부 내용은 기존 문서 체계를 그대로 사용합니다.
   - 구현 세부: `docs/daily/`
   - 테스트: `docs/testing/`
   - 실험: `docs/experiments/`
   - 기준선 변경: `docs/adr/`
4. 새 채팅에서 작업을 시작할 때는 최근 `docs/archive/HISTORY.md` 항목을 먼저 읽고 현재 기준선을 파악합니다.
5. 실험 세션은 `docs/archive/HISTORY.md` 요약과 `docs/experiments/` 실제 로그를 함께 남기는 방식으로 운영합니다.

## 근거

1. 누적 요약과 세부 로그를 분리하면, 빠른 파악과 상세 추적을 동시에 만족할 수 있습니다.
2. 별도 채팅으로 넘어가더라도 프로젝트 상태를 짧게 복원할 수 있습니다.
3. 기존 `docs/planning/08_DOCUMENTATION_POLICY.md`와 충돌하지 않고, 운영 수준의 보강으로 적용할 수 있습니다.

## 결과

1. 앞으로 완료 보고는 `docs/archive/HISTORY.md`와 세부 로그를 함께 갱신한 상태를 기준으로 합니다.
2. 실험/구현/문서화가 여러 세션에 나뉘어도, `docs/archive/HISTORY.md`를 보면 현재 위치를 빠르게 파악할 수 있습니다.
3. 누적 히스토리 갱신이 누락되면 세션 완료로 보지 않습니다.

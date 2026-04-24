# testing 가이드

`docs/testing/`에는 탐색 기록부터 발표 직전 freeze 검증까지 문서가 많이 쌓여 있습니다.  
발표나 포트폴리오 확인 기준으로는 전부 읽을 필요가 없습니다.

참고로 오래된 문서에는 채널 연동 화면이 `/accounts`로 적혀 있을 수 있습니다. 현재 공개 기준선에서는 이 화면을 `/channels`로 정리했고, `/accounts`는 legacy redirect만 남겨 두었습니다.

## 먼저 볼 문서

1. [test-scenario-186-root-selective-integration-freeze.md](test-scenario-186-root-selective-integration-freeze.md)  
   현재 trunk 기준선에서 로그인, 생성, 결과 확인, 게시 fallback, worker 경계를 어떻게 검증했는지 정리한 문서입니다.
2. [shin-vm-origin-verification-and-backup.md](shin-vm-origin-verification-and-backup.md)  
   신유철 VM 원본, trunk 스냅샷 일치, GCP 환경, 백업 범위를 확인한 문서입니다.
3. [test-scenario-185-user-test-script-simple-flow.md](test-scenario-185-user-test-script-simple-flow.md)  
   발표 리허설이나 사용자 설명에 바로 쓸 수 있는 간단한 흐름 문서입니다.

## 나머지 문서의 성격

- `test-scenario-01` ~ `test-scenario-99`  
  초기 MVP, UI, API, 생성 흐름을 검토한 기록입니다.
- `test-scenario-100` 이후  
  copy/prompt/video 방향 실험과 세부 정책 검토가 중심입니다.

즉, 발표 관점에서는 `186 + shin-vm + 185-user-test`만 읽어도 현재 기준선 설명에는 충분합니다.

## 발표 기준 검증 분류

| 구분 | 현재 말할 수 있는 범위 | 대표 근거 |
|---|---|---|
| 자동화 검증 | API 테스트 27개, worker 테스트 85개, web typecheck/build 통과 | 루트 `npm run check`, `services/api/tests`, `services/worker/tests` |
| 수동 리허설 | 로그인, 생성, 결과 확인, 업로드 보조, 이력 재진입 흐름 확인 | `test-scenario-186`, `test-scenario-185-user-test` |
| 외부 VM 실험 근거 | Wan2.1-VACE 원본 VM, trunk 스냅샷 커밋 일치, 대표 산출물/로그 존재 확인 | `shin-vm-origin-verification-and-backup.md` |
| 보류 리스크 | 운영 인프라, 전체 SNS 자동 게시, Wan2.1-VACE 앱 기본 런타임 직접 대체는 후속 과제 | `test-scenario-186`, `Project-report.md` |

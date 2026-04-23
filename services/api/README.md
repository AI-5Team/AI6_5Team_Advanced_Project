# API Service

백엔드 API 서버 위치입니다.

- 프로젝트 생성/조회
- 상태 조회
- 업로드/예약 요청 등록
- SNS 계정 연동 상태 관리

## Known Limitations (MVP 데모 환경 기준)

다음 항목들은 의도적으로 MVP 범위에서 제외했으며, 운영 배포 전 처리 예정입니다.

### 운영 배포 전 필수

- [ ] **레이트리밋 Redis 이전**
  현재 인메모리 슬라이딩 윈도우 방식. 멀티 인스턴스 환경에서 카운트 분산 안 됨.

- [ ] **OAuth 토큰 갱신 Race Condition 방어**
  `get_valid_access_token()` 동시 호출 시 refresh 충돌 가능성.
  Redis 분산 락으로 해결 예정 (`services/api/app/services/crypto.py` TODO 참조).

- [ ] **회원 탈퇴 시 도메인 전체 정리**
  자동화 팀의 예약 업로드 작업 정지 로직 추가 필요. (자동화 팀 작업 완료 후 통합)

- [ ] **정책 개정 시 재동의 강제 플로우**
  현재 약관 버전 1개. 개정 발생 시점에 구현.

### Post-MVP 강화 항목

- [ ] Secret Manager 연동 (현재 환경변수)
- [ ] 정책 문서 CMS 분리 (현재 정적 페이지)
- [ ] Audit log HMAC 익명화 (현재 NULL)
- [ ] 2FA / Passkey / 소셜 로그인
- [ ] 활성 세션 목록 UI


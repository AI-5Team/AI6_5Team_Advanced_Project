# Worker Service

비동기 작업 처리 서비스 위치입니다.

- 이미지 전처리
- 카피 생성
- 숏폼 렌더링
- 업로드 및 예약 발행 실행
- `Wan2.1-VACE` 실험 스냅샷은 `external/i2v-motion-experiments`에 보존되어 있습니다.
- trunk 연동은 `services/worker/adapters/adapter_wan2_vace.py`의 subprocess 경계로만 진행합니다.
- 기본 환경 변수 예시는 루트 `.env.example`의 `WORKER_WAN_VACE_*` 항목을 참고하시면 됩니다.

# 테스트 시나리오 14 - HTML/CSS Scene Lab 빌드 검증

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-14`

## 2. 테스트 목적

- 새 `/scene-lab` 페이지와 샘플 자산 API 라우트가 빌드에 포함되는지 확인합니다.

## 3. 사전 조건

- `docs/sample` 실제 음식 사진 존재
- web workspace 빌드 가능 상태

## 4. 수행 항목

1. `npm run build:web`
2. build route 목록에서 `/scene-lab`, `/api/sample-assets/[sample]` 확인

## 5. 결과

- build: 통과
- 확인된 route:
  - `/scene-lab`
  - `/api/sample-assets/[sample]`

## 6. 관찰 내용

- HTML/CSS prototype 경로가 web 앱에 정상 포함됐습니다.
- 샘플 사진을 web 쪽에서 직접 불러오는 API 경로도 함께 빌드됐습니다.

## 7. 실패/제약

1. 이번 검증은 build 기준이며, 브라우저 시각 검증은 별도 수행하지 않았습니다.
2. 아직 worker 렌더 파이프라인과 연결되지 않았습니다.

## 8. 개선 포인트

1. 다음 단계는 browser screenshot/capture를 붙여 실제 프레임 비교를 하는 것입니다.

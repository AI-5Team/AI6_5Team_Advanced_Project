# ADR-010 루트 저장소를 trunk로 고정하고 기능 선별 통합을 적용한다

- 상태: 승인
- 날짜: 2026-04-16

## 배경

팀원별로 API, worker, 모델 실험, 프론트 화면이 서로 다른 저장소와 폴더에 분산되어 있습니다.  
현재 시점에서 폴더 단위 병합을 수행하면 다음 문제가 커집니다.

1. `services/api/app`, `apps/web`, `packages/contracts` 기준선이 흔들립니다.
2. UI 프레임워크가 섞이면서 발표 직전 trunk 안정성이 떨어집니다.
3. 모델 실험 저장소가 제품 런타임에 직접 스며들어 실행 조건이 불명확해집니다.

## 결정

1. 현재 루트 저장소를 trunk로 고정합니다.
2. 폴더 단위 병합은 금지하고 기능 단위 선별 이식만 허용합니다.
3. 프론트는 `apps/web`만 유지하고, 외부 Vite UI는 화면 흐름과 자산만 포팅합니다.
4. worker는 기존 구조를 유지하되 `adapters / pipelines / renderers` 경계를 더 분명히 합니다.
5. 모델 실험 저장소는 독립 유지하고, 제품 런타임에는 adapter/subprocess 경계로만 연결합니다.
6. freeze 전까지 채택/보류/폐기와 검증 결과를 문서화합니다.

## 근거

1. 루트 저장소는 이미 API 계약, planning 문서, Next.js 앱, worker 기준 구조를 갖추고 있습니다.
2. 발표 기준선은 "모든 기능이 가장 강한 부분만 섞인 상태"보다 "설명 가능한 trunk 하나"가 더 중요합니다.
3. 실험 저장소를 직접 import하지 않는 방식이 재현성과 운영 안정성에 유리합니다.

## 결과

1. trunk의 source of truth는 `packages/contracts + docs/planning + services/api/app + apps/web`로 정리됩니다.
2. 로그인/UI 통합과 모델 연결은 trunk 내부에서 각자 독립적으로 진행할 수 있습니다.
3. freeze 전 검증 시나리오와 채택 판정표가 통합 작업의 필수 산출물이 됩니다.

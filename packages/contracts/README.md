# Contracts

프론트엔드와 백엔드가 공유하는 계약 정의 위치입니다.

- enum
- 상태값
- API 예시 payload
- 공통 스키마

## 구조

```text
contracts/
├─ enums/
├─ schemas/
├─ examples/
└─ index.ts
```

## 사용 원칙

1. Web, API, Worker는 enum을 하드코딩하지 않고 여기서 가져옵니다.
2. 상태값을 바꾸면 `docs/planning/04_API_CONTRACT.md`도 같이 수정합니다.
3. 예시 payload는 `examples/`를 source of truth로 간주합니다.
4. `generationRunId`, `uploadJobId`, `scheduleJobId` 같은 식별자 명칭은 문서와 동일하게 유지합니다.
5. `schemas/auth.ts`, `schemas/schedule.ts`, `schemas/uploadAssist.ts`는 Phase 1 MVP에 필요한 누락 계약을 보완합니다.
6. `schemas/generation.ts`의 `ProjectResultResponse`는 `copyPolicy`, `copyDeck`, `sceneLayerSummary`, `changeImpactSummary`, `promptBaselineSummary` 같은 결과 해석 메타데이터도 함께 포함합니다.

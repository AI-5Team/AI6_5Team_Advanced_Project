# EXP-258 Evidence-Based Hybrid Lane Hint

## 1. 기본 정보

- 실험 ID: `EXP-258`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `approved hybrid lane hint를 businessType 단일 규칙에서 evidence-based scoring으로 확장`

## 2. 왜 이 작업을 했는가

- `EXP-257`까지의 lane hint는 `cafe -> drink`, `restaurant -> tray` 수준이라, 실제 업로드 자산과 inventory label 근거가 화면에 드러나지 않았습니다.
- 이 상태에서는 추천 lane이 나와도 “왜 이 lane인가”를 설명하기 어려워 운영 기준으로는 약했습니다.
- 따라서 이번 단계에서는 approved inventory label, 업로드 파일명, businessType, templateId를 함께 점수화하는 helper를 추가해 hint의 근거를 명시적으로 보여주도록 바꿨습니다.

## 3. 이번에 바꾼 것

1. `apps/web/src/lib/hybrid-lane-hint.ts`
   - evidence-based lane hint helper를 새로 추가했습니다.
   - 입력 신호:
     - `businessType`
     - `templateId`
     - `assetFileNames`
     - `approvedInventoryLabels`
   - 현재 scoring:
     - `cafe -> drink_glass_lane (+2)`
     - `restaurant -> tray_full_plate_lane (+2)`
     - `T02 + restaurant -> tray_full_plate_lane (+1)`
     - `approved inventory label match in fileName (+4)`
     - `generic drink/tray keyword match in fileName (+2)`
   - 결과로 `lane`, `confidence`, `evidence[]`, `scoreByLane`, `recommendedCandidateKey`를 돌려줍니다.
2. `apps/web/src/components/demo-workbench.tsx`
   - simple businessType rule 대신 위 helper를 사용하도록 바꿨습니다.
   - UI에는 추천 lane과 confidence, 파일명 기반 근거, approved label match 근거를 함께 노출합니다.
   - 근거가 비슷하거나 부족하면 lane을 강하게 밀지 않고 `명확한 lane hint가 없습니다` 상태를 보여줍니다.

## 4. 실행 및 검증

```bash
npm run lint:web
npm run build:web
```

결과:

- 타입 체크 통과
- Next production build 통과

## 5. 결과

1. 이제 lane hint는 단순 업종 규칙이 아니라, 실제 업로드 자산 파일명과 approved inventory label을 함께 반영합니다.
2. 예를 들어 파일명에 `맥주`, `규카츠`처럼 inventory에 이미 존재하는 label이 들어 있으면 가장 강한 근거로 lane을 제안할 수 있습니다.
3. 동시에 잘못된 자동화는 피하기 위해, helper는 추천만 하고 candidate attach는 여전히 자동으로 수행하지 않습니다.

## 6. 해석

1. 이번 단계는 lane hint를 “규칙”에서 “근거가 보이는 scoring”으로 올린 작업입니다.
2. 다만 아직 파일명 기반 신호가 약하거나 없는 경우가 있기 때문에, 이것만으로 완전한 자동 선택까지 가기에는 부족합니다.
3. 다음 단계에서 자동 추천 강도를 높이려면 asset composition 분류나 lane annotation 데이터가 더 필요합니다.

## 7. 결론

- approved hybrid baseline 선택 흐름은 이제 lane filter UI를 넘어, `왜 이 lane을 먼저 보라고 하는지`까지 설명 가능한 상태가 됐습니다.
- 다음 우선순위는 `asset/lane annotation 또는 분류 신호 추가`이거나, `tray/full-plate lane approved 후보 확장`입니다.

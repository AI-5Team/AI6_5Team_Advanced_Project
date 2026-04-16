# EXP-257 Approved Hybrid Lane Hint UI

## 1. 기본 정보

- 실험 ID: `EXP-257`
- 작성일: `2026-04-14`
- 작성자: Codex
- 관련 기능: `approved hybrid inventory 선택 부담을 줄이기 위한 lane hint / lane filter / 추천 candidate 적용 UI`

## 2. 왜 이 작업을 했는가

- `EXP-256`으로 approved inventory를 web generate 흐름에서 직접 소비할 수는 있게 됐지만, 운영자는 여전히 모든 candidate를 직접 훑어야 했습니다.
- 지금 단계의 병목은 후보 수가 너무 많아서가 아니라, 어떤 lane을 먼저 봐야 하는지 판단 기준이 화면에 없다는 점이었습니다.
- 따라서 이번 단계에서는 hidden automation 대신, 임시 lane hint 규칙과 lane filter를 UI에 노출해 운영자가 더 빠르게 기준선을 고를 수 있게 만들었습니다.

## 3. 이번에 바꾼 것

1. `apps/web/src/components/demo-workbench.tsx`
   - `inferHybridServiceLaneHint()`를 추가했습니다.
   - 현재 임시 규칙:
     - `cafe -> drink_glass_lane`
     - `restaurant -> tray_full_plate_lane`
   - 이 규칙은 어디까지나 `hint`이며, candidate를 자동으로 generate 요청에 붙이지는 않습니다.
2. approved inventory 선택 UI 보강
   - lane별 filter 버튼을 추가했습니다.
   - 현재 wizard 설정 기준 추천 lane과 추천 candidate를 따로 보여줍니다.
   - `추천 candidate 적용` 버튼을 눌러야만 실제 `approvedHybridSourceCandidateKey`가 선택됩니다.
3. candidate select 동작 정리
   - lane filter가 켜져 있으면 해당 lane의 candidate만 select에 보이도록 했습니다.
   - candidate를 직접 고르면 해당 candidate의 lane도 같이 맞춰집니다.

## 4. 실행 및 검증

```bash
npm run lint:web
npm run build:web
```

결과:

- 타입 체크 통과
- Next production build 통과

## 5. 결과

1. 운영자는 이제 전체 candidate 목록을 무작정 보는 대신, lane부터 먼저 좁히고 후보를 고를 수 있습니다.
2. wizard 설정 기준 추천 lane과 추천 candidate가 화면에 드러나기 때문에, 현재 문맥에서 어떤 baseline을 먼저 볼지 판단이 빨라집니다.
3. 하지만 여전히 자동 attach는 하지 않으므로, 잘못된 규칙이 본선 generate를 오염시키는 문제는 피했습니다.

## 6. 해석

1. 이번 단계는 “자동 추천”보다 “추천 기준의 가시화”에 가깝습니다.
2. 즉 product flow에서는 기준선 소비를 더 쉽게 만들었지만, 잘못된 자동화를 넣지는 않았습니다.
3. 다음 단계에서 정말 자동 추천까지 가려면, 지금의 단순 `businessType` 규칙 대신 asset composition 또는 lane annotation 근거가 더 필요합니다.

## 7. 결론

- approved hybrid baseline은 이제 단순 선택 dropdown이 아니라, lane 기준으로 탐색 가능한 운영 UI가 됐습니다.
- 다만 현 lane hint 규칙은 임시 수준이므로, 다음 우선순위는 `lane hint 규칙의 근거 강화` 또는 `tray/full-plate lane 후보 추가 확보`입니다.

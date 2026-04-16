# Test Scenario 97 - reference teardown pattern matrix

## 목적

- `EXP-95`가 외부 레퍼런스에서 뽑아낸 패턴을 실제 backlog 우선순위로 제대로 바꿨는지 확인합니다.

## 입력 자료

1. `docs/experiments/EXP-94-reference-first-video-direction-review.md`
2. `docs/experiments/EXP-95-reference-teardown-pattern-matrix.md`
3. `docs/experiments/EXP-90-upper-bound-video-benchmark-pilot.md`
4. `docs/experiments/EXP-91-sora2-motion-prompt-family-ovaat.md`
5. `docs/experiments/EXP-92-sora2-input-framing-ovaat.md`
6. `docs/experiments/EXP-93-sora2-edit-motion-recovery-ovaat.md`

## 절차

1. `EXP-95`의 매트릭스를 읽고 각 레퍼런스가 `가져올 수 있는 것`과 `못 가져오는 것`으로 분리됐는지 확인합니다.
2. `EXP-90`~`EXP-93`을 다시 읽고, 왜 `prompt OVAT`가 하위 우선순위로 내려가는지 납득 가능한지 점검합니다.
3. `EXP-95`의 다음 우선순위 3개를 읽고, 각 우선순위가 본선 또는 연구선에 어떤 가치를 주는지 확인합니다.
4. 아래 질문에 예/아니오로 답합니다.
   - 지금 당장 가져와야 하는 핵심은 model quality보다 hook/shot/workflow grammar인가
   - strict preserve와 creative reinterpretation을 분리해야 하는가
   - next backlog가 raw prompt digging보다 reference-derived backlog 쪽으로 이동했는가

## 기대 결과

1. 다음 backlog가 `reference-derived hook`, `objective split`, `input modality change` 중심으로 재정렬됩니다.
2. 현재 프로젝트에서 외부 사례를 그대로 복제하는 것이 아니라, 필요한 요소만 추출한다는 원칙이 유지됩니다.
3. 본선과 연구선의 평가 기준이 섞이지 않도록 다시 한 번 고정됩니다.

## 판정 기준

- 아래 3개가 모두 맞으면 통과입니다.
  1. `EXP-95`가 backlog 재정렬 문서 역할을 하는가
  2. 레퍼런스 차용 범위와 한계를 둘 다 명시했는가
  3. 다음 액션이 문서상 3~4개 수준으로 구체화됐는가

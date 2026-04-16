# Test Scenario 98 - reference template-fit scorecard

## 목적

- `EXP-96`의 채점표가 앞으로 찾는 외부 광고 레퍼런스를 일관되게 분류하는 기준으로 쓸 수 있는지 확인합니다.

## 입력 자료

1. `docs/experiments/EXP-95-reference-teardown-pattern-matrix.md`
2. `docs/experiments/EXP-96-reference-template-fit-scorecard.md`

## 절차

1. `EXP-96`의 7개 채점 항목을 읽습니다.
2. 새로운 레퍼런스 하나를 골라 빠른 판정용 시트를 채워 봅니다.
3. 총점에 따라 `템플릿 적합`, `부분 차용`, `상한선 참고` 중 하나로 분류합니다.
4. 분류 뒤 아래를 확인합니다.
   - 본선 backlog로 바로 올릴지
   - 일부만 차용할지
   - 연구선 reference로만 둘지

## 기대 결과

1. 레퍼런스 평가 기준이 `좋아 보임`에서 `템플릿 적합도`로 바뀝니다.
2. 본선 backlog와 연구 reference가 섞이지 않게 됩니다.
3. 앞으로 레퍼런스 수집량이 늘어나도 같은 기준으로 빠르게 걸러낼 수 있습니다.

## 판정 기준

- 아래 3개가 모두 맞으면 통과입니다.
  1. 채점 기준이 템플릿 목적에 직접 연결되는가
  2. 최종 분류가 backlog 우선순위 결정에 실제로 쓰일 수 있는가
  3. `부분 차용`과 `상한선 참고`가 구분되는가

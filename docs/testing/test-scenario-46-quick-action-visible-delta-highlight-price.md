# 테스트 시나리오 46 - Quick Action Visible Delta (highlightPrice)

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-46`

## 2. 테스트 목적

- 실제 프로젝트 생성 후 `가격 강조(highlightPrice)`가 regenerate 결과에 눈에 띄는 차이를 만드는지 확인합니다.

## 3. 수행 항목

1. `node scripts/capture_quick_action_delta.mjs --lever highlightPrice --output-dir docs/experiments/artifacts/exp-43-quick-action-visible-delta-highlight-price`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-43-quick-action-visible-delta-highlight-price/summary.json`
  - `baseline-s2.png`
  - `highlight-price-s2.png`

## 5. 관찰 내용

1. `s2` benefit scene의 primary text가 가격 중심 표현으로 바뀌었습니다.
2. opening/CTA는 그대로이고, benefit scene 변화가 핵심입니다.
3. 따라서 `highlightPrice`는 scene-specific delta를 만든다고 볼 수 있습니다.

## 6. 실패/제약

1. 실제 숫자 가격/할인율은 들어가지 않습니다.
2. 현재는 `가격 메리트` 수준의 copy shift입니다.

## 7. 개선 포인트

1. 업로드 보조와 첫 결과 생성 시간 점검으로 본선 검증을 이어가야 합니다.
2. 가격 action 강도는 structured offer 데이터가 준비되면 다시 올릴 수 있습니다.

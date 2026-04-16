# 테스트 시나리오 61 - local LTX baseline multi-image validation

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-61`

## 2. 테스트 목적

- 현재 LTX baseline이 여러 실제 음식 사진에서도 비슷하게 유지되는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_baseline_multi_image_validation.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-58-local-ltx-baseline-multi-image-validation/summary.json`
  - 각 이미지별 `ltx_first_try_mid_frame.png`

## 5. 관찰 내용

1. 규카츠는 비교적 안정적이었습니다.
2. 라멘, 순두부짬뽕, 장어덮밥은 품질 편차가 컸습니다.
3. 따라서 현재 baseline은 음식군 일반화에 실패했다고 보는 편이 맞습니다.

## 6. 실패/제약

1. 4장 기준입니다.
2. seed 편차는 아직 포함하지 않았습니다.

## 7. 개선 포인트

1. 다음에는 같은 음식에 대해 seed 안정성을 봅니다.
2. 음식군별 prompt template 분리 필요성도 검토합니다.

# 테스트 시나리오 70 - local LTX preserve-shot top bias OVAT

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-70`

## 2. 테스트 목적

- preserve-shot 그룹에서 `contain_blur`보다 `cover_top`이 더 좋은 하위 타입이 있는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_preserve_shot_top_bias_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-67-local-ltx-preserve-shot-top-bias-ovaat/summary.json`

## 5. 관찰 내용

1. `cover_top`은 `커피` 1건을 제외하면 전반적으로 더 나빴습니다.
2. 특히 `라멘`, `장어덮밥`은 `contain_blur`를 유지하는 편이 확실히 낫습니다.
3. 따라서 `cover_top`은 preserve-shot 일반 정책이 아니라, drink 예외 후보 정도로만 남습니다.

## 6. 실패/제약

1. drink 샘플이 `커피` 1장뿐입니다.
2. seed `7` 고정 기준입니다.

## 7. 개선 포인트

1. 다음은 전역 변경이 아니라 `커피만 cover_top` 예외 policy를 확인해야 합니다.
2. regression 없이 작은 개선을 얻을 수 있는지 보는 것이 목적입니다.

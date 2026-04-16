# 테스트 시나리오 69 - local LTX prepare_mode policy split

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-69`

## 2. 테스트 목적

- global `contain_blur`보다 `샷 타입 -> prepare_mode` 분기 policy가 single-photo 조건에서 더 나은 baseline인지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_prepare_mode_policy_split.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-66-local-ltx-prepare-mode-policy-split/summary.json`

## 5. 관찰 내용

1. `규카츠`는 `cover_center` 예외가 더 좋았습니다.
2. 나머지 5장은 global `contain_blur`와 동일 품질을 유지했습니다.
3. 즉 `규카츠=cover_center`, 나머지=`contain_blur` policy가 global baseline보다 안전합니다.

## 6. 실패/제약

1. 실제로 바뀐 샘플은 `규카츠` 1건뿐입니다.
2. seed `7` 고정 기준입니다.

## 7. 개선 포인트

1. 다음은 preserve-shot 안에서 `cover_top` 같은 예외가 있는지 봐야 합니다.
2. 특히 `drink`나 `dessert` 쪽은 추가 예외 가능성이 있습니다.

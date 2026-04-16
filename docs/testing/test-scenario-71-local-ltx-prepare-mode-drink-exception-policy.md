# 테스트 시나리오 71 - local LTX prepare_mode drink exception policy

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-71`

## 2. 테스트 목적

- 기존 prepare_mode policy(`규카츠=cover_center`, 그 외=`contain_blur`)에 `커피만 cover_top` 예외를 추가했을 때 regression 없이 이득이 있는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_prepare_mode_drink_exception.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-68-local-ltx-prepare-mode-drink-exception-policy/summary.json`

## 5. 관찰 내용

1. `커피`에서만 `cover_top`이 더 좋았습니다.
2. 나머지 5장은 기존 policy와 동일했습니다.
3. 즉 `커피만 cover_top` 예외는 작은 개선을 회귀 없이 추가합니다.

## 6. 실패/제약

1. drink 일반화 근거는 아직 부족합니다.
2. seed `7` 고정 기준입니다.

## 7. 개선 포인트

1. 현재는 `drink general rule`보다 `glass drink candidate rule`로 보는 편이 맞습니다.
2. 다음은 shot type auto classification이나 drink 샘플 추가 확보가 필요합니다.

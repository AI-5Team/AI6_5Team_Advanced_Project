# 테스트 시나리오 68 - local LTX framing mode OVAT

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-68`

## 2. 테스트 목적

- 사용자가 실제로 가지고 있는 `식사 중 스냅 사진 1장` 조건에서, prompt보다 입력 프레이밍 방식이 더 큰 레버인지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_framing_mode_ovaat.py --offline`

## 4. 결과

- 실행 상태: 성공
- artifact:
  - `exp-65-local-ltx-framing-mode-ovaat/summary.json`

## 5. 관찰 내용

1. `contain_blur`가 `6개 중 5개`에서 더 나았습니다.
2. 특히 라멘, 순두부짬뽕, 장어덮밥처럼 원본 구도를 더 많이 보존해야 하는 사진에서 차이가 컸습니다.
3. 규카츠처럼 이미 꽉 찬 트레이샷은 `cover_center`가 더 낫습니다.

## 6. 실패/제약

1. `contain_blur`는 배경 패드가 들어가서 edge variance 수치는 낮게 나오는 경향이 있습니다.
2. seed `7` 고정입니다.

## 7. 개선 포인트

1. 다음 baseline은 `prepare_mode`를 샷 타입에 따라 분기해야 합니다.
2. 같은 프롬프트를 더 깎기 전에, 입력 프레이밍 분기를 먼저 정하는 편이 맞습니다.

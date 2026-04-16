# 테스트 시나리오 43 - Local LTX Prompt Length OVAT

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-43`

## 2. 테스트 목적

- `LTX-Video 2B / GGUF`에서 `prompt length`만 바꿨을 때 실제 품질 차이가 생기는지 확인합니다.

## 3. 수행 항목

1. `python scripts/local_video_ltx_first_try.py --num-frames 17 --steps 6 --fps 8 --output-dir docs/experiments/artifacts/exp-40-local-ltx-video-prompt-length-ovaat/default-prompt`
2. `python scripts/local_video_ltx_first_try.py --num-frames 17 --steps 6 --fps 8 --prompt "crispy gyukatsu, gentle steam, slow push-in, warm restaurant lighting, realistic food motion" --output-dir docs/experiments/artifacts/exp-40-local-ltx-video-prompt-length-ovaat/short-prompt`
3. warm cache 비교
   - `HF_HUB_OFFLINE=1`로 default/short prompt 재실행

## 4. 결과

- 두 실행 모두 성공
- warm cache 기준 short prompt가 더 안정적이었습니다.

## 5. 관찰 내용

1. short prompt는 mid frame에서 음식 구조 보존이 더 좋았습니다.
2. default prompt는 잔상/고스팅이 더 큽니다.

## 6. 실패/제약

1. 첫 short prompt 실행 시간은 HF retry 때문에 오염됐습니다.
2. 단일 이미지 기준입니다.

## 7. 개선 포인트

1. `LTX` baseline prompt는 앞으로 짧고 직접적인 문장으로 가는 편이 좋습니다.

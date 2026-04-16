# 테스트 시나리오 36 - Local Video Model Feasibility Review

## 1. 테스트 정보

- 일자: `2026-04-08`
- 진행자: Codex
- 시나리오 ID: `TS-36`

## 2. 테스트 목적

- `RTX 4080 Super 16GB / RAM 64GB` 환경에서 어떤 생성형 비디오 모델을 먼저 보는 것이 맞는지 공식 자료 기준으로 분류합니다.

## 3. 수행 항목

1. `nvidia-smi`
2. 공식 문서/모델 카드 검토
   - `Wan2.2-I2V-A14B`
   - `Wan2.2-TI2V-5B`
   - `LTX-2 image-to-video guide`
   - `LTX-Video official repo`
   - `Diffusers LTX-Video`
   - `Diffusers CogVideoX`
   - `Diffusers Mochi`

## 4. 결과

- 로컬 하드웨어 baseline 확인: 완료
- feasibility matrix 문서화: 완료
- 생성 문서:
  - `EXP-32-local-video-model-feasibility-matrix-4080super.md`

## 5. 관찰 내용

1. `Wan2.2-I2V-A14B`, `LTX-2.3`는 지금 장비의 first try 후보가 아니었습니다.
2. `LTX-Video 2B distilled / GGUF`가 가장 현실적인 첫 후보입니다.
3. `CogVideoX-5B-I2V`는 느리더라도 두 번째 후보군입니다.

## 6. 실패/제약

1. 이번 테스트는 문서/모델 카드 기반 feasibility 검토입니다.
2. 실제 비디오 생성 benchmark는 아직 아닙니다.

## 7. 개선 포인트

1. 다음 단계는 `LTX-Video 2B distilled` 실제 로컬 실행입니다.
2. 그 다음 `CogVideoX-5B-I2V`를 같은 장비 기준으로 붙입니다.

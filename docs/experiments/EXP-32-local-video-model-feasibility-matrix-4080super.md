# EXP-32 Local Video Model Feasibility Matrix For RTX 4080 Super 16GB

## 1. 기본 정보

- 실험 ID: `EXP-32`
- 작성일: `2026-04-08`
- 작성자: Codex
- 관련 기능: `로컬 생성형 비디오 모델 후보 정리`

## 2. 왜 이 작업을 했는가

- 사용자는 `RTX 4080 Super 16GB / RAM 64GB` 기준에서 실제로 돌릴 수 있는 다른 모델들도 함께 보고 싶다고 요청했습니다.
- 팀원 한 분이 `Wan2.2-I2V-A14B`, `LTX-2.3`를 이미 써봤다고 공유했고, 그래서 “지금 장비에서 바로 실험 가능한 후보”와 “지금 장비에는 무거운 후보”를 분리할 필요가 생겼습니다.
- 이 문서는 아직 코드 통합 문서가 아니라, **다음 비디오 실험 우선순위를 다시 고정하는 feasibility 문서**입니다.

## 3. 로컬 하드웨어 baseline

- GPU: `NVIDIA GeForce RTX 4080 Super 16GB`
- RAM: `64GB`
- 드라이버/쿠다: `Driver 595.71 / CUDA 13.2`
- 확인 명령:
  - `nvidia-smi`

## 4. 확인한 공식 자료

- [Wan2.2-I2V-A14B model card](https://huggingface.co/Wan-AI/Wan2.2-I2V-A14B)
- [Wan2.2-TI2V-5B model card](https://huggingface.co/Wan-AI/Wan2.2-TI2V-5B)
- [LTX-2 image-to-video guide](https://docs.ltx.video/open-source-model/usage-guides/image-to-video)
- [LTX-Video official repo](https://github.com/Lightricks/LTX-Video)
- [Diffusers LTX-Video docs](https://huggingface.co/docs/diffusers/en/api/pipelines/ltx_video)
- [Diffusers CogVideoX guide](https://huggingface.co/docs/diffusers/main/en/using-diffusers/cogvideox)
- [Diffusers Mochi docs](https://huggingface.co/docs/diffusers/main/en/api/pipelines/mochi)

## 5. 결과

### 후보별 판단

| 후보 | 공식 자료 기준 | 4080S 16GB 판단 | 이번 우선순위 |
|---|---|---|---|
| `Wan2.2-I2V-A14B` | Wan2.2 A14B 계열은 MoE 기반 고품질 라인이고, 공식 자료도 A14B는 multi-GPU oriented 문맥이 강함 | **현재 로컬 first try 부적합** | 뒤로 미룸 |
| `Wan2.2-TI2V-5B` | 공식 카드 기준 `720P@81f`는 `single GPU 4090 24GB` 예시가 제시됨 | **16GB는 공식 단일 GPU 기준보다 아래** | 보류 |
| `LTX-2.3 / LTX-2` | 공식 open-source I2V 가이드에서 `At least 32GB recommended` | **16GB 직접 실험 비우선** | 뒤로 미룸 |
| `LTX-Video 2B distilled / GGUF / FP8` | 공식 repo가 `2B distilled`, `FP8`, `GGUF`, temporal windowing을 모두 제공 | **16GB에서 가장 먼저 볼 후보** | 1순위 |
| `CogVideoX-5B(-I2V)` | 공식 diffusers 가이드가 `CPU offload`, `VAE tiling/slicing` 경로를 제공 | **느리지만 시도 가능한 후보** | 2순위 |
| `Mochi 1 Preview` | 공식 diffusers 문서 기준 `bf16 22GB`, full precision `42GB` | **16GB 부적합** | 제외 |

### 핵심 해석

1. `Wan2.2-I2V-A14B`와 `LTX-2.3`를 팀이 이미 만져본 것은 의미가 있습니다.
2. 다만 **이 둘을 4080 Super 16GB에서 바로 주력 로컬 baseline으로 잡는 건 맞지 않습니다.**
3. 현재 장비에서 첫 실험 우선순위는 `LTX-Video 2B distilled / GGUF / FP8`처럼 경량화된 LTX 계열입니다.
4. 그 다음 후보는 `CogVideoX-5B-I2V`입니다. 공식 가이드가 offload/tiling/slicing 경로를 제공하므로, 느리더라도 실험 가치가 있습니다.
5. `Wan2.2-TI2V-5B`는 “완전 제외”는 아니지만, 공식 single-GPU 예시가 이미 `24GB`라서 16GB에서 바로 들어가면 삽질 가능성이 높습니다.

## 6. 실패/제약

1. 이번 문서는 feasibility 정리 문서라서, 아직 실제 비디오 생성 실행까지는 하지 않았습니다.
2. `LTX-2.3`의 정확한 16GB local benchmark를 공식 문서에서 찾지는 못했습니다.
   - 따라서 `16GB 부적합` 판단은 `LTX-2 open-source guide의 32GB recommended`를 근거로 한 **보수적 추론**입니다.
3. `Wan2.2-I2V-A14B`도 exact VRAM 숫자보다는 공식 card/repo의 A14B 고급 라인, multi-GPU 지향 문맥을 근거로 판단했습니다.

## 7. 결론

- 가설 충족 여부: **충족**
- 판단:
  - 팀원이 본 `Wan2.2-I2V-A14B`, `LTX-2.3`를 그대로 따라가는 것보다, **현재 장비에 맞는 더 가벼운 비디오 후보부터 실험하는 것이 맞습니다.**
  - 지금 장비에서는 `LTX-Video 2B distilled` 계열이 가장 먼저 볼 가치가 큽니다.
  - `CogVideoX-5B-I2V`는 느리더라도 두 번째 후보로 볼 수 있습니다.
  - `Wan2.2-I2V-A14B`, `LTX-2.3`는 로컬 baseline이 아니라 **고성능 장비/공유 벤치마크 lane**으로 두는 게 맞습니다.

## 8. 다음 액션

1. 다음 비디오 실험 1순위는 `LTX-Video 2B distilled / GGUF`입니다.
2. 다음 비디오 실험 2순위는 `CogVideoX-5B-I2V`입니다.
3. `Wan2.2-TI2V-5B`는 16GB 로컬이 아니라, 더 큰 VRAM 장비나 클라우드가 확보될 때 다시 검토합니다.
4. `Wan2.2-I2V-A14B`, `LTX-2.3`는 이번 로컬 baseline 라인에서는 제외합니다.

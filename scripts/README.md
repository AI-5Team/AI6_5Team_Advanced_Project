# Scripts

개발/실험/배치 보조 스크립트 위치입니다.

- `generate_sample_assets.py`: 데모/테스트용 입력 이미지를 생성합니다.
- `run_prompt_experiment.py`: production 경로를 바꾸지 않고 프롬프트 레버 실험을 실행합니다.
- `run_video_experiment.py`: production renderer를 바꾸지 않고 영상 레이아웃 실험을 실행합니다.
- `hosted_video_veo31_first_try.py`: Veo 3.1 image-to-video upper-bound 파일럿을 실행합니다.
- `hosted_video_sora2_first_try.py`: Sora 2 image-to-video upper-bound 파일럿을 실행합니다.
- `video_upper_bound_benchmark.py`: local LTX와 hosted upper-bound(Veo 3.1, Sora 2)를 같은 샘플/프롬프트로 비교하는 파일럿 benchmark를 실행합니다.
- `sora2_motion_prompt_family_ovaat.py`: `맥주` 샘플에서 Sora 2 motion prompt family를 OVAT로 비교하고 baseline/manual Veo reference와 함께 요약합니다.
- `sora2_input_framing_ovaat.py`: `맥주` 샘플에서 Sora 2 입력 프레이밍 zoom variant를 OVAT로 비교하고 baseline/manual Veo reference와 함께 요약합니다.
- `sora2_edit_motion_recovery_ovaat.py`: `hero_tight` Sora 결과를 source로 다시 edit해 motion recovery 가능성을 OVAT로 비교합니다.
- `run_prompt_repeatability_spot_check.py`: 고정 prompt/model subset을 여러 번 실행해 hook/CTA 길이와 over-limit 안정성을 빠르게 점검합니다. `--experiment-id` 기준으로 `exp-<source>-repeatability.json` artifact를 남깁니다.
- `rescore_location_surface_policy.py`: 기존 artifact를 다시 읽어 nearby-location leakage를 surface 정책별(`strict_all_surfaces`, `public_copy_surfaces`, `distribution_surfaces`)로 재채점합니다.

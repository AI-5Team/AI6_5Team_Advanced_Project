# Trunk Snapshot

이 디렉토리는 신유철님의 모델 실험 저장소를 trunk 안에 **보존용 스냅샷**으로 반입한 경로입니다.

- 원본 저장소: `https://github.com/youuuchul/i2v-motion-experiments`
- 반입 기준 commit: `6ea9ffc060655b2eadf394e5b98e85dc89aaec8e`
- 반입 일자: `2026-04-23`

## 포함 범위

- `apps/`
- `configs/`
- `docker/`
- `docs/`
- `scripts/`
- `src/`
- `tests/`
- `.env.example`
- `.gitignore`
- `README.md`
- `pyproject.toml`

## 제외 범위

- `.git/`
- 모델 weight / cache / checkpoint
- `outputs/`, `logs/`, `runs/`, `mlruns/`
- 개인 샘플 이미지와 외부 밈 원본 자산
- Google Drive 산출물

## trunk 원칙

- 웹/API는 이 경로를 직접 import 하지 않습니다.
- worker 는 `services/worker/adapters/adapter_wan2_vace.py`를 통해
  `scripts/run_inference.py --config ...` 형태로만 호출합니다.
- 발표/문서/인수인계 기준선은 **이 스냅샷 + 메인 README + docs/daily 기록**입니다.

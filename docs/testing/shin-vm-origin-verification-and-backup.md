# 신유철 VM 원본 검증 및 백업

## 목적

신유철 모델 실험이 실제로 남아 있는 VM 원본과, 현재 trunk에 보존한 스냅샷이 같은 기준선인지 확인하고, 발표에 필요한 최소 증거를 별도 백업으로 확보합니다.

## 확인 일시

- 2026-04-23

## 확인 환경

- GCP project: `sprint-ai-chunk2-04`
- VM: `instance-20260413-060635`
- zone: `us-central1-c`
- external IP: `34.123.200.68`
- VM OS: Debian GNU/Linux 12
- GPU: NVIDIA L4 24GB

## 확인한 항목

### 1. 원본 실험 경로 존재

아래 경로가 실제로 존재하는 것을 확인했습니다.

- `/home/youuchul/work/i2v-motion-experiments`

또한 `/home` 아래에 `youuchul` 계정과 작업 디렉토리가 남아 있었습니다.

### 2. trunk 스냅샷과 VM 원본 커밋 일치

VM 안에서 아래 명령으로 원본 레포 커밋을 확인했습니다.

```bash
git -C /home/youuchul/work/i2v-motion-experiments rev-parse --short HEAD
```

결과:

- `6ea9ffc`

이 값은 현재 trunk에 보존한 [TRUNK_SNAPSHOT.md](../../external/i2v-motion-experiments/TRUNK_SNAPSHOT.md)의 기준 커밋과 일치합니다.

즉, **메인 레포에 보존한 신유철 실험 스냅샷은 VM 원본 기준과 같은 버전**입니다.

### 3. GPU 상태 확인

`nvidia-smi` 기준으로 GPU는 정상 인식되었습니다.

- GPU: `NVIDIA L4`
- Driver: `595.58.03`
- CUDA Version: `13.2`
- 확인 시점에는 실행 중인 GPU 프로세스 없음

의미:

- VM이 죽은 상태는 아니었고
- 적어도 하드웨어 기준으로는 실험 환경이 남아 있었습니다.

### 4. Docker 상태 확인

`sudo docker ps -a` 기준으로 아래 상태를 확인했습니다.

- `streamlit` 컨테이너: `Up`
- `batch` 컨테이너: `Exited`
- 이전 `i2v_run_*` 계열 컨테이너: `Exited`

해석:

- Streamlit 결과 뷰어는 계속 살아 있습니다.
- 다만 확인 시점에 batch 추론이 실제로 돌아가고 있지는 않았습니다.

### 5. 실험 결과와 로그 존재

아래 경로들에 실험 결과와 로그가 남아 있었습니다.

- `outputs/`
- `logs/`

확인한 대표 결과 폴더 예시는 아래입니다.

- `outputs/wan_vace_beer_dolly_in`
- `outputs/wan_vace_pizza_dolly_in`
- `outputs/wan_vace_pizza_lift_to_camera`
- `outputs/wan_vace_sample_consume_product`
- `outputs/wan_vace_sample_steam_rise`

확인한 로그 예시는 아래입니다.

- `logs/orchestrator.log`
- `logs/relaunch_watcher.log`
- `logs/wrapper_batch9.log`
- `logs/wrapper_round9_ext.log`
- `logs/infer_wan21_vace_142313.log`
- `logs/infer_wan21_vace_retry*.log`

## 백업 범위

VM 전체를 옮기지는 않았고, 발표와 근거 보존에 필요한 최소 범위만 묶었습니다.

### 포함

- commit 정보
- `nvidia-smi` 출력
- `docker ps -a` 출력
- `README.md`, `pyproject.toml`, `.env.example`
- `docs/`
- `configs/`
- `outputs/index.jsonl`
- 주요 로그 파일
- 대표 산출물 폴더 일부

### 제외

- 모델 weight / cache
- 전체 `outputs/` 폴더
- VM 전체 파일 시스템
- 실행 중이 아닌 오래된 불필요 컨테이너 데이터

## 백업 결과

Cloud Shell로 아래 백업 번들을 가져왔습니다.

- `shin_vm_backup_2026-04-23.tar.gz`

압축본 크기:

- 약 `2.6MB`

즉, **원본 VM이 나중에 정리되더라도 발표와 검증 근거에 필요한 핵심 자료는 별도 확보한 상태**입니다.

## 지금 이 문서로 말할 수 있는 것

1. 신유철 모델 실험은 실제 GCP VM에서 수행된 것이 맞습니다.
2. 현재 trunk 스냅샷은 VM 원본 레포와 같은 커밋 기준입니다.
3. Streamlit 뷰어, 결과 폴더, 로그까지 실제로 남아 있는 것을 확인했습니다.
4. 발표용으로 필요한 최소 근거는 별도 백업해 두었습니다.

## 조심해서 말해야 하는 것

아래는 여전히 선을 그어야 합니다.

1. 신유철 실험이 현재 앱 런타임에 직접 붙어 있는 것은 아닙니다.
2. 확인 시점에 batch 추론이 돌고 있지는 않았습니다.
3. 이번 백업은 전체 VM 아카이브가 아니라, 발표와 기록 보존용 최소 번들입니다.

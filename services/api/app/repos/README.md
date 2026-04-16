# Repos Layer Status

현재 freeze 기준선에서는 `repos` 레이어를 아직 사용하지 않습니다.

## 현재 원칙

- DB access source of truth는 `app.core.database` + `app.services.runtime`입니다.
- 실제 쿼리는 현재 `runtime.py`에 직접 들어 있습니다.
- 업무 재분배 이후 필요할 때만 `repos`로 분리합니다.

## 주의

- freeze 전에는 새 DB 접근 코드를 임의로 ORM/repository 패턴으로 옮기지 않습니다.
- 공용 계약 변경 없이 필요한 수정은 현재 runtime 경로에서만 반영합니다.

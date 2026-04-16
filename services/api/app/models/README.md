# Models Layer Status

현재 API 기준선은 **raw sqlite3** 기반입니다.

## freeze 기준

- `app.core.database`의 sqlite schema와 `get_connection()`이 현재 DB source of truth입니다.
- SQLAlchemy ORM 모델은 이번 freeze 기준선에서 제거했습니다.
- 따라서 `models` 디렉토리는 향후 post-freeze 구조 정리를 위한 자리만 남겨둡니다.

## 주의

- freeze 전에는 새 ORM 모델을 추가하지 않습니다.
- DB 스키마 변경이 필요하면 먼저 `app.core.database`와 planning 문서를 함께 갱신합니다.

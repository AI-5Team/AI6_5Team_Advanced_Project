# packages/auth-core

자동화 팀을 위한 OAuth 토큰 인터페이스 패키지입니다.

## 핵심 원칙

- `getValidAccessToken` **한 함수만 export** 합니다.
- `decryptToken` / `encryptToken`은 내부 전용 — 이 패키지에서 절대 export하지 않습니다.
- 평문 토큰은 함수 내부에서만 존재합니다. 로그나 에러 메시지에 노출될 위험이 없습니다.

## 사용법 (자동화 팀)

```python
from packages.auth_core import get_valid_access_token, NotConnectedError

# 유효한 OAuth 액세스 토큰을 반환합니다.
# 만료 5분 전이면 자동으로 갱신합니다.
# 연결되지 않았거나 갱신 불가능하면 NotConnectedError를 발생시킵니다.
try:
    token = get_valid_access_token(user_id="abc123", provider="instagram")
    # token을 Instagram API 호출에 사용
except NotConnectedError:
    # 사용자에게 SNS 재연결 안내
    ...
```

## 인터페이스

```python
def get_valid_access_token(user_id: str, provider: str) -> str:
    """
    파라미터:
        user_id  — users.id (UUID 문자열)
        provider — "instagram" | "youtube_shorts" | "tiktok"

    반환값:
        유효한 OAuth 액세스 토큰 (평문 문자열)

    예외:
        NotConnectedError — 연결 없음, 만료 후 갱신 불가

    주의:
        반환된 토큰을 로그, 에러 메시지, 직렬화에 포함하지 마세요.
        함수 내부에서 즉시 API 호출에만 사용하세요.
    """
```

## 모노레포 내 위치

```
services/api/app/services/crypto.py  ← 실제 구현체
packages/auth-core/                  ← 이 패키지 (인터페이스 명세)
```

현재는 Python 모노레포 구조이므로 직접 import 경로를 사용합니다:

```python
# services/worker 또는 다른 서비스에서
import sys
sys.path.insert(0, "services/api")
from app.services.crypto import get_valid_access_token, NotConnectedError
```

## 운영 전환 전 필수 작업

- [ ] `get_valid_access_token()` 내부에 Redis 분산 락 추가
  - 동시 갱신 요청 시 refresh token 충돌 방지
  - `services/api/app/services/crypto.py` TODO 주석 참조

## export 통제 이유

자동화 팀이 `decrypt_token()`을 직접 호출할 수 있으면:
1. 평문 토큰이 변수에 살아있는 시간이 길어짐
2. 에러 처리 중 로그에 노출될 위험
3. 다른 컨텍스트에서 복호화 로직이 복사·재사용될 위험

`get_valid_access_token()` 한 함수만 제공함으로써 평문 토큰의 생명주기를 제한합니다.

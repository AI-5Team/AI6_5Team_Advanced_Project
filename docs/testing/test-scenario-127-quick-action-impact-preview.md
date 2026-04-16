# Test Scenario 127 - Quick Action Impact Preview

## 목적

- quick action 버튼이 영향 레이어와 설명을 미리 보여주면서도 빌드가 깨지지 않는지 확인합니다.

## 확인 항목

1. quick action cards
   - 각 버튼 아래에 영향 레이어 chip이 보입니다.
   - 각 버튼 아래에 영향 설명 문구가 보입니다.
2. shared helper
   - `demo-store`와 quick action UI가 같은 impact descriptor helper를 사용합니다.
3. web build
   - 새 helper와 quick action 카드 확장 후에도 타입 오류 없이 빌드됩니다.

## 실행

```powershell
npm run build:web
```

## 기대 결과

- 사용자는 regenerate 버튼을 누르기 전부터 각 quick action이 어떤 층을 바꾸는지 미리 읽을 수 있습니다.

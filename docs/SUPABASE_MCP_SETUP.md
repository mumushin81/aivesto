# Supabase MCP 설정 가이드

## 개요

Supabase MCP (Model Context Protocol)를 통해 Claude AI 어시스턴트가 자연어로 Supabase 데이터베이스와 상호작용할 수 있습니다.

**⚠️ 중요: 개발 환경 전용**
- 이 설정은 **로컬 개발 환경에서만** 사용하세요
- 프로덕션 데이터베이스에는 **절대** 사용하지 마세요
- 보안 위험: Prompt injection, 예상치 못한 쿼리 실행 가능

## 설치 완료 사항

### 1. Supabase MCP 서버 설치

```bash
npm install -g @supabase/mcp-server-supabase
```

✅ 설치 완료: 2025년 공식 Supabase MCP 서버

### 2. Claude Desktop 설정

위치: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "supabase": {
      "command": "npx",
      "args": [
        "-y",
        "@supabase/mcp-server-supabase"
      ],
      "env": {
        "SUPABASE_URL": "https://czubqsnahmtdsmnyawlk.supabase.co",
        "SUPABASE_ANON_KEY": "[YOUR_ANON_KEY]"
      }
    }
  }
}
```

✅ 설정 완료: Aivesto 프로젝트에 연결됨

## 사용 가능한 기능

### 1. 문서 검색
```
"Supabase에서 Row Level Security 설정하는 방법 알려줘"
```

MCP가 최신 Supabase 공식 문서를 검색하여 답변합니다.

### 2. TypeScript 타입 생성
```
"데이터베이스 스키마에서 TypeScript 타입 생성해줘"
```

현재 데이터베이스 스키마 기반으로 자동 타입 생성합니다.

### 3. 데이터베이스 조회
```
"최근 7일간 생성된 뉴스 기사 수를 조회해줘"
```

자연어로 SQL 쿼리를 생성하여 실행합니다.

### 4. 스키마 탐색
```
"현재 데이터베이스의 모든 테이블과 컬럼 구조를 보여줘"
```

### 5. 마이그레이션 생성
```
"articles 테이블에 sentiment 컬럼을 추가하는 마이그레이션 생성해줘"
```

## 안전 사용 가이드

### ✅ 권장 사용 사례

1. **스키마 탐색**
   - 테이블 구조 확인
   - 관계 이해
   - 인덱스 확인

2. **타입 생성**
   - TypeScript 타입 자동 생성
   - 프론트엔드 개발에 활용

3. **문서 검색**
   - Supabase 기능 학습
   - 베스트 프랙티스 확인

4. **개발 데이터 분석**
   - 테스트 데이터 통계
   - 임시 리포트 생성

5. **마이그레이션 초안**
   - 스키마 변경 계획
   - SQL 생성 보조

### ❌ 피해야 할 사용

1. **프로덕션 데이터 변경**
   - INSERT, UPDATE, DELETE 쿼리
   - 실제 사용자 데이터 수정

2. **민감 정보 조회**
   - 사용자 개인정보
   - 인증 토큰
   - API 키

3. **무분별한 쿼리**
   - 전체 테이블 스캔
   - 복잡한 JOIN 쿼리 (성능 영향)

4. **자동화 워크플로우**
   - CI/CD 파이프라인
   - 스케줄된 작업

## 보안 설정

### 현재 설정 (Anon Key)
- 읽기 전용 권한
- Row Level Security (RLS) 정책 적용
- 공개 데이터만 접근 가능

### 추가 보안 강화 (선택사항)

#### 1. 개발 브랜치 생성
```bash
# Supabase CLI 설치
npm install -g supabase

# 개발 브랜치 생성
supabase branches create dev-mcp

# MCP를 dev 브랜치에만 연결
# SUPABASE_URL을 브랜치 URL로 변경
```

#### 2. Read-Only 사용자 생성
```sql
-- PostgreSQL에서 읽기 전용 사용자 생성
CREATE ROLE mcp_readonly WITH LOGIN PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE postgres TO mcp_readonly;
GRANT USAGE ON SCHEMA public TO mcp_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT ON TABLES TO mcp_readonly;
```

## 트러블슈팅

### MCP 서버 연결 실패
1. Claude Desktop 완전 종료 후 재시작
2. 설정 파일 JSON 문법 확인
3. Supabase URL과 키 재확인

### 쿼리 실행 권한 오류
- Row Level Security 정책 확인
- Anon key 권한 범위 확인
- 테이블별 권한 설정 검토

### 느린 응답 속도
- MCP는 API ↔ Claude ↔ Supabase 경로로 동작
- 복잡한 쿼리는 직접 API 사용 권장

## 대안: 직접 API 사용

프로덕션 환경이나 성능이 중요한 경우:

```python
# 권장: Supabase Python 클라이언트 직접 사용
from supabase import create_client

supabase = create_client(
    supabase_url=os.getenv("SUPABASE_URL"),
    supabase_key=os.getenv("SUPABASE_KEY")
)

# 타입 안전하고 예측 가능한 쿼리
response = supabase.table('articles') \
    .select('*') \
    .gte('created_at', '2025-01-01') \
    .execute()
```

## Claude Desktop 재시작

설정 변경 후:
1. Claude Desktop 완전 종료
2. Activity Monitor에서 Claude 프로세스 확인 및 종료
3. Claude Desktop 재시작
4. MCP 도구 사용 가능 확인

## 참고 문서

- [Supabase MCP 공식 문서](https://supabase.com/docs/guides/getting-started/mcp)
- [Model Context Protocol 스펙](https://modelcontextprotocol.io/)
- [Supabase CLI 가이드](https://supabase.com/docs/guides/cli)

## 마지막 업데이트

- 날짜: 2025-01-15
- 버전: @supabase/mcp-server-supabase (latest)
- 프로토콜: MCP 2025-06-18

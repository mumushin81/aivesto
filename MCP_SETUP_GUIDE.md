# Supabase MCP 설정 가이드

이 가이드는 Claude Code에서 Supabase MCP (Model Context Protocol) 서버를 설정하는 방법을 설명합니다.

## 1. 사전 준비

### Supabase 프로젝트 설정

1. [Supabase](https://supabase.com)에 로그인
2. 프로젝트 생성 또는 기존 프로젝트 선택
3. **Settings → API**에서 다음 정보 확인:
   - Project URL: `https://your-project.supabase.co`
   - `anon` public key
   - `service_role` secret key (서버용)

### 데이터베이스 스키마 생성

1. Supabase 대시보드에서 **SQL Editor** 열기
2. `database/schema.sql` 파일의 내용을 복사하여 붙여넣기
3. **Run** 클릭하여 테이블 및 인덱스 생성

생성되는 테이블:
- `news_raw`: 원본 뉴스 데이터 (24시간 TTL)
- `analyzed_news`: 분석된 뉴스 데이터
- `published_articles`: 발행된 블로그 글
- `articles`: 다층적 수집 데이터 (Layer 1/2/3)
- `signals`: 투자 신호 데이터

## 2. 환경 변수 설정

`.env` 파일이 이미 프로젝트 루트에 생성되어 있습니다:

```bash
# Supabase Configuration
SUPABASE_URL=https://czubqsnahmtdsmnyawlk.supabase.co
SUPABASE_KEY=your_service_role_key
SUPABASE_ANON_KEY=your_anon_key
```

**주의**: `.env` 파일은 `.gitignore`에 포함되어 있어 Git에 커밋되지 않습니다.

## 3. MCP 서버 설정

### Claude Desktop 설정

MCP 설정 파일이 자동으로 생성되었습니다:

**위치**: `~/.config/Claude/claude_desktop_config.json` (Linux)

```json
{
  "mcpServers": {
    "supabase": {
      "command": "python3",
      "args": [
        "/home/user/aivesto/mcp_server.py"
      ],
      "env": {
        "SUPABASE_URL": "https://czubqsnahmtdsmnyawlk.supabase.co",
        "SUPABASE_KEY": "your_service_role_key"
      }
    }
  }
}
```

### MCP 서버 기능

`mcp_server.py`는 다음 메서드를 지원합니다:

#### 대시보드 통계
- `get_dashboard_stats`: 전체 통계 조회
- `get_articles_for_dashboard`: 대시보드용 기사 목록
- `get_price_impact_summary`: 가격 영향도 요약

#### 뉴스 분석
- `get_high_relevance_news`: 높은 관련성 뉴스
- `get_recent_articles`: 최근 발행 글
- `get_important_symbols_today`: 오늘 주목할 종목

#### 신호 및 트렌드
- `get_signals_by_level`: 신호 레벨별 조회
- `get_signals_by_symbol`: 종목별 신호 조회
- `get_trending_symbols`: 트렌딩 종목

## 4. 연결 테스트

패키지 설치:
```bash
pip install -r requirements.txt
```

연결 테스트 실행:
```bash
python3 test_supabase_connection.py
```

성공적인 연결 시 다음과 같은 출력이 표시됩니다:
```
✓ Supabase client initialized successfully
✓ Dashboard stats retrieved
✓ Trending symbols retrieved
✓ Articles retrieved
🎉 All tests passed! Supabase connection is working.
```

## 5. Claude Code에서 사용

Claude Code를 재시작하면 Supabase MCP 서버가 자동으로 로드됩니다.

Claude에게 다음과 같이 요청할 수 있습니다:

```
"Supabase에서 최근 24시간 동안의 고우선순위 뉴스를 가져와줘"
"오늘 트렌딩 종목 상위 10개를 보여줘"
"Level 1 신호가 있는 뉴스를 조회해줘"
```

## 6. 문제 해결

### 403 Access Denied 에러

데이터베이스 테이블이 없거나 RLS(Row Level Security) 정책이 잘못 설정된 경우:

1. Supabase SQL Editor에서 `schema.sql` 재실행
2. RLS 정책 확인:
   ```sql
   -- 모든 사용자 읽기 권한
   CREATE POLICY "Enable read access for all users"
   ON news_raw FOR SELECT USING (true);
   ```

### MCP 서버가 로드되지 않는 경우

1. Claude Desktop 재시작
2. `claude_desktop_config.json` 경로 확인
3. Python 경로 확인: `which python3`
4. MCP 서버 직접 실행:
   ```bash
   python3 mcp_server.py
   ```

### 패키지 설치 오류

가상 환경 사용 권장:
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## 7. 다음 단계

1. **데이터 수집**: `collectors/` 디렉토리의 수집기 실행
2. **뉴스 분석**: `analyzers/` 디렉토리의 분석기 실행
3. **대시보드 실행**: `dashboard/` 디렉토리의 웹 대시보드 실행
4. **자동화**: `scheduler/` 디렉토리의 스케줄러 설정

## 참고 자료

- [Supabase 문서](https://supabase.com/docs)
- [MCP 프로토콜](https://modelcontextprotocol.io/)
- [Claude Code 문서](https://docs.anthropic.com/claude/docs)

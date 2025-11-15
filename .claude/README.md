# Claude Code MCP 설정

## Supabase MCP Server

이 프로젝트는 Supabase MCP (Model Context Protocol) 서버를 사용하여 AI가 데이터베이스와 직접 상호작용할 수 있습니다.

### 설정 파일

- **mcp.json**: MCP 서버 구성 파일
  - Supabase MCP 서버 URL: `https://mcp.supabase.com/mcp`
  - **읽기 전용 모드**: `read_only=true` (안전성을 위해)
  - **활성화된 기능**: `database`, `docs`

### 인증 방법

MCP 서버는 OAuth 2.1 인증을 사용합니다. Claude Code를 재시작하면 자동으로 Supabase 로그인 프롬프트가 표시됩니다.

### 보안 주의사항

⚠️ **중요**: Supabase MCP는 **개발 및 테스트 목적으로만** 사용하세요.
- 프로덕션 데이터에 연결하지 마세요
- 읽기 전용 모드로 실행 권장
- 특정 프로젝트로 범위 제한 권장

### 설정 커스터마이징

`mcp.json` 파일에서 URL 쿼리 파라미터를 수정할 수 있습니다:

```json
{
  "url": "https://mcp.supabase.com/mcp?read_only=true&project_ref=YOUR_PROJECT_ID&features=database,docs"
}
```

**사용 가능한 파라미터:**
- `read_only=true` - 읽기 전용 쿼리만 허용
- `project_ref=<id>` - 특정 프로젝트로 제한
- `features=database,docs` - 활성화할 도구 그룹

**사용 가능한 기능 그룹:**
- `account` - 계정 관리
- `database` - 데이터베이스 쿼리
- `debugging` - 디버깅 도구
- `development` - 개발 도구
- `docs` - 문서
- `functions` - Edge Functions
- `branching` - 브랜치 관리

### 문제 해결

MCP 서버가 작동하지 않으면:

1. Claude Code 재시작
2. 브라우저에서 Supabase 로그인 완료
3. `.env` 파일에 Supabase URL과 Key가 올바르게 설정되어 있는지 확인

### 참고 자료

- [Supabase MCP 공식 문서](https://supabase.com/docs/guides/getting-started/mcp)
- [GitHub: supabase-community/supabase-mcp](https://github.com/supabase-community/supabase-mcp)

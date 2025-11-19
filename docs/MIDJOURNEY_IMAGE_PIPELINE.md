# Midjourney → Supabase → Blog 자동화 가이드

## 준비물
- Python 3.10+
- `pip install -r requirements.txt`
- `.env`에 다음 값 설정
  - `DISCORD_BOT_TOKEN`
  - `MIDJOURNEY_CHANNEL_ID`
  - `MIDJOURNEY_BOT_ID` (기본 936929561302675456)
  - `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` (또는 `SUPABASE_KEY`)
- `config/midjourney_bot.yaml` 생성 (`config/midjourney_bot.example.yaml` 참고)
- Supabase DB/스토리지에 스키마 반영: `supabase db push --file database/midjourney_blog_schema.sql`

## 실행 흐름
1) `scripts/run_image_pipeline.py`
   - `scripts/ai_image_prompts.json`을 읽어 Discord 채널에 `/imagine` 전송
   - Midjourney 응답 이미지 수신 → 로컬 임시 저장 → Supabase Storage 업로드
   - `images` / `blog_images` 테이블에 메타데이터 기록
   - 새로운 카드 블록을 `public/blog.html` 상단에 주입

## 명령어 예시
```bash
export DISCORD_BOT_TOKEN=...    # .env에도 저장 가능
export MIDJOURNEY_CHANNEL_ID=123456789012345678
python scripts/run_image_pipeline.py
```

## 파일 설명
- `scripts/discord_midjourney_bot.py` : Midjourney 자동화 Discord 봇
- `scripts/supabase_image_uploader.py` : 스토리지 업로드 + DB 기록
- `scripts/blog_image_injector.py` : blog.html 카드 삽입
- `scripts/run_image_pipeline.py` : 전체 파이프라인 실행기
- `database/midjourney_blog_schema.sql` : Supabase 스키마
- `config/midjourney_bot.example.yaml` : 설정 템플릿

## 주의 (ToS/위험)
- Midjourney/Discord 자동화는 약관 위반 위험이 있으므로 개인 서버에서만 사용하고, 상업적/대규모 발송은 피하세요.
- 빈번한 요청은 Midjourney 속도 제한 및 계정 제재를 유발할 수 있습니다. `rate_limit_per_min`로 조절하세요.
- 공식 API 사용이 가능하다면 해당 경로를 우선 고려하세요.

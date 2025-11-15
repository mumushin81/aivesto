#!/usr/bin/env python3
"""
블로그 기사를 Supabase published_articles 테이블에 업로드
"""
import os
import sys
import glob
from datetime import datetime

# 프로젝트 루트를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.supabase_client import SupabaseClient


def parse_article(file_path):
    """마크다운 파일 파싱"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # TITLE: / CONTENT: 형식 파싱
    title = 'Untitled'
    article_content = content

    if 'TITLE:' in content and 'CONTENT:' in content:
        title_start = content.find('TITLE:') + len('TITLE:')
        content_start = content.find('CONTENT:')
        title = content[title_start:content_start].strip()
        article_content = content[content_start + len('CONTENT:'):].strip()
    else:
        # 기존 방식: H1 제목 추출
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                title = line.replace('#', '').strip()
                break

    # 파일명에서 심볼과 날짜 추출
    filename = os.path.basename(file_path)
    symbol = None
    date_str = None

    # 파일명 형식: article_SYMBOL_description_YYYYMMDD.md
    if '_' in filename:
        parts = filename.split('_')
        if len(parts) > 1:
            symbol = parts[1]  # 2번째 부분이 SYMBOL

        # 파일명 끝에서 날짜 추출 (20251113 형식)
        filename_no_ext = filename.replace('.md', '')
        if len(filename_no_ext) >= 8 and filename_no_ext[-8:].isdigit():
            date_part = filename_no_ext[-8:]
            try:
                date_str = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
            except:
                pass

    return {
        'title': title,
        'content': article_content,
        'symbol': symbol,
        'published_at': date_str,
        'filename': filename
    }


def upload_articles(db_client, articles_dir):
    """모든 기사를 Supabase에 업로드"""
    article_files = glob.glob(os.path.join(articles_dir, 'article_*.md'))

    print(f"\n{'='*60}")
    print(f"📤 Uploading Articles to Supabase")
    print(f"{'='*60}\n")

    uploaded_count = 0
    skipped_count = 0
    error_count = 0

    for file_path in sorted(article_files):
        try:
            article = parse_article(file_path)

            # Supabase에 삽입
            data = {
                'title': article['title'],
                'content': article['content'],
                'published_at': article['published_at'] or datetime.now().isoformat(),
                'metadata': {
                    'symbol': article['symbol'],
                    'filename': article['filename'],
                    'source': 'local_upload',
                    'format': 'TITLE_CONTENT'
                }
            }

            # 중복 확인 (제목으로)
            existing = db_client.client.table('published_articles') \
                .select('id') \
                .eq('title', article['title']) \
                .execute()

            if existing.data:
                print(f"⏭️  SKIP: {article['filename']} (이미 존재)")
                skipped_count += 1
                continue

            # 삽입
            result = db_client.client.table('published_articles').insert(data).execute()

            if result.data:
                print(f"✅ UPLOADED: {article['filename']}")
                print(f"   Symbol: {article['symbol']}, Title: {article['title'][:50]}...")
                uploaded_count += 1
            else:
                print(f"❌ FAILED: {article['filename']}")
                error_count += 1

        except Exception as e:
            print(f"❌ ERROR: {article['filename']} - {e}")
            error_count += 1

    print(f"\n{'='*60}")
    print(f"📊 Upload Summary")
    print(f"{'='*60}")
    print(f"✅ Uploaded: {uploaded_count}")
    print(f"⏭️  Skipped: {skipped_count}")
    print(f"❌ Errors: {error_count}")
    print(f"📂 Total Files: {len(article_files)}")
    print(f"{'='*60}\n")


def main():
    # Supabase 연결
    try:
        db = SupabaseClient()
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Failed to connect to Supabase: {e}")
        print("\n⚠️  Please configure Supabase credentials in .env:")
        print("   SUPABASE_URL=https://xxx.supabase.co")
        print("   SUPABASE_KEY=your_anon_key")
        sys.exit(1)

    # 기사 디렉토리
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    articles_dir = os.path.join(base_dir, 'articles')

    if not os.path.exists(articles_dir):
        print(f"❌ Articles directory not found: {articles_dir}")
        sys.exit(1)

    # 업로드
    upload_articles(db, articles_dir)


if __name__ == '__main__':
    main()

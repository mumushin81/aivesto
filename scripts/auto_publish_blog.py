#!/usr/bin/env python3
"""
자동 블로그 발행 파이프라인
1. E2E 파이프라인 실행 (뉴스 수집 및 분석)
2. Supabase에서 high-priority 시그널 찾기
3. 블로그 글 작성
4. Supabase에 업로드
5. 정적 HTML 생성
"""
import os
import sys
import subprocess

# 프로젝트 루트를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.supabase_client import SupabaseClient
from scripts.ai_writer import generate_article


def run_e2e_pipeline():
    """E2E 파이프라인 실행"""
    print("\n" + "=" * 60)
    print("Step 1: Running E2E Pipeline (News Collection & Analysis)")
    print("=" * 60 + "\n")

    result = subprocess.run(
        ["python3", "pipeline/run_e2e.py"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("✅ E2E Pipeline completed successfully")
        return True
    else:
        print(f"❌ E2E Pipeline failed: {result.stderr}")
        return False


def find_high_priority_signals(db_client, min_score=80, limit=5):
    """High-priority 시그널 찾기"""
    print("\n" + "=" * 60)
    print(f"Step 2: Finding High-Priority Signals (Score >= {min_score})")
    print("=" * 60 + "\n")

    try:
        signals = db_client.client.table('signals') \
            .select('*') \
            .gte('priority_score', min_score) \
            .order('priority_score', desc=True) \
            .order('created_at', desc=True) \
            .limit(limit) \
            .execute()

        if signals.data:
            print(f"✅ Found {len(signals.data)} high-priority signals:")
            for signal in signals.data:
                print(f"  - [{signal['priority_score']}점] {signal['title'][:60]}...")
            return signals.data
        else:
            print(f"⚠️  No signals found with score >= {min_score}")
            return []
    except Exception as e:
        print(f"❌ Error finding signals: {e}")
        return []


def check_article_exists(db_client, signal_title):
    """이미 작성된 기사인지 확인"""
    try:
        existing = db_client.client.table('published_articles') \
            .select('id') \
            .ilike('title', f'%{signal_title[:30]}%') \
            .execute()

        return len(existing.data) > 0
    except Exception as e:
        print(f"⚠️  Error checking existing article: {e}")
        return False


def write_articles(signals):
    """블로그 기사 작성"""
    print("\n" + "=" * 60)
    print("Step 3: Writing Blog Articles")
    print("=" * 60 + "\n")

    articles_written = []

    for i, signal in enumerate(signals, 1):
        print(f"\n[{i}/{len(signals)}] Processing: {signal['title'][:60]}...")

        try:
            # 기사 작성
            article_path = generate_article(signal)

            if article_path and os.path.exists(article_path):
                print(f"✅ Article written: {os.path.basename(article_path)}")
                articles_written.append(article_path)
            else:
                print(f"⚠️  Failed to write article for: {signal['title'][:60]}")

        except Exception as e:
            print(f"❌ Error writing article: {e}")

    return articles_written


def upload_to_database(articles):
    """Supabase에 업로드"""
    print("\n" + "=" * 60)
    print("Step 4: Uploading Articles to Supabase")
    print("=" * 60 + "\n")

    result = subprocess.run(
        ["python3", "scripts/upload_articles_to_db.py"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(result.stdout)
        print("✅ Upload completed")
        return True
    else:
        print(f"❌ Upload failed: {result.stderr}")
        return False


def generate_static_html():
    """정적 HTML 생성"""
    print("\n" + "=" * 60)
    print("Step 5: Generating Static HTML")
    print("=" * 60 + "\n")

    result = subprocess.run(
        ["python3", "scripts/generate_static_blog.py"],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print(result.stdout)
        print("✅ HTML generation completed")
        return True
    else:
        print(f"❌ HTML generation failed: {result.stderr}")
        return False


def main():
    print("\n" + "=" * 60)
    print("🤖 Aivesto Auto Blog Publishing Pipeline")
    print("=" * 60)

    # Supabase 연결
    db_client = SupabaseClient()

    # 1. E2E 파이프라인 실행
    if not run_e2e_pipeline():
        print("\n❌ Pipeline failed at E2E stage. Exiting.")
        return

    # 2. High-priority 시그널 찾기
    signals = find_high_priority_signals(db_client, min_score=80, limit=5)

    if not signals:
        print("\n⚠️  No high-priority signals found. Nothing to write.")
        return

    # 이미 작성된 기사 필터링
    new_signals = []
    for signal in signals:
        if not check_article_exists(db_client, signal['title']):
            new_signals.append(signal)
        else:
            print(f"⏭️  SKIP (already exists): {signal['title'][:60]}...")

    if not new_signals:
        print("\n⚠️  All signals already have articles. Nothing to write.")
        return

    print(f"\n✅ {len(new_signals)} new articles to write")

    # 3. 블로그 기사 작성
    articles = write_articles(new_signals)

    if not articles:
        print("\n⚠️  No articles were written. Exiting.")
        return

    print(f"\n✅ {len(articles)} articles written successfully")

    # 4. Supabase에 업로드
    if not upload_to_database(articles):
        print("\n⚠️  Upload failed, but articles are saved locally.")

    # 5. 정적 HTML 생성
    if not generate_static_html():
        print("\n⚠️  HTML generation failed.")
        return

    # 최종 요약
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    print(f"✅ Processed {len(signals)} high-priority signals")
    print(f"✅ Written {len(articles)} new articles")
    print(f"✅ Articles saved to: articles/")
    print(f"✅ HTML generated to: public/articles/")
    print("=" * 60 + "\n")

    print("🚀 Ready for deployment!")
    print("   1. Review articles in articles/ directory")
    print("   2. Commit and push to GitHub")
    print("   3. Vercel will auto-deploy")


if __name__ == '__main__':
    main()

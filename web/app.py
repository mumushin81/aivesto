#!/usr/bin/env python3
"""
간단한 블로그 뷰어 웹 애플리케이션
"""
import os
import sys
from flask import Flask, render_template, send_from_directory, jsonify, request
import markdown
import glob
from datetime import datetime

# 프로젝트 루트를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.supabase_client import SupabaseClient

app = Flask(__name__)

# 프로젝트 루트 디렉토리
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_DIR = os.path.join(BASE_DIR, 'articles')

# Supabase 클라이언트 (선택적)
try:
    db_client = SupabaseClient()
    DB_ENABLED = True
    print("✅ Supabase connected")
except Exception as e:
    db_client = None
    DB_ENABLED = False
    print(f"⚠️  Supabase not available: {e}")

def parse_article(file_path):
    """마크다운 파일을 파싱하여 메타데이터와 콘텐츠 추출"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # TITLE: 과 CONTENT: 레이블 제거 및 파싱
    title = 'Untitled'
    article_content = content

    if 'TITLE:' in content and 'CONTENT:' in content:
        # TITLE: 과 CONTENT: 사이의 텍스트가 제목
        title_start = content.find('TITLE:') + len('TITLE:')
        content_start = content.find('CONTENT:')
        title = content[title_start:content_start].strip()

        # CONTENT: 이후의 모든 내용이 본문
        article_content = content[content_start + len('CONTENT:'):].strip()
    else:
        # 기존 방식: H1 제목 추출
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                title = line.replace('#', '').strip()
                break

    # HTML 변환
    html_content = markdown.markdown(article_content, extensions=['tables', 'fenced_code', 'attr_list'])

    # 파일명에서 종목 코드와 날짜 추출
    filename = os.path.basename(file_path)
    symbol = None
    date = '2025-11-13'

    # 파일명 형식: article_SYMBOL_description_YYYYMMDD.md
    if '_' in filename:
        parts = filename.split('_')
        if len(parts) > 1:
            symbol = parts[1]  # 2번째 부분이 SYMBOL
        # 파일명 끝에서 날짜 추출 (20251113 형식)
        filename_no_ext = filename.replace('.md', '')
        if len(filename_no_ext) >= 8 and filename_no_ext[-8:].isdigit():
            date_str = filename_no_ext[-8:]
            date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    return {
        'title': title,
        'date': date,
        'content': html_content,
        'filename': filename,
        'symbol': symbol,
        'file_path': file_path
    }

@app.route('/')
def index():
    """메인 페이지: 실시간 대시보드로 리다이렉트"""
    if DB_ENABLED:
        return render_template('dashboard.html')
    else:
        # DB 없으면 기존 블로그 보기
        return blog_index()


@app.route('/blog')
def blog_index():
    """블로그 페이지: 모든 기사 목록"""
    # 모든 마크다운 파일 찾기
    article_files = glob.glob(os.path.join(ARTICLES_DIR, 'article_*.md'))

    # 파싱
    articles = []
    for file_path in sorted(article_files, reverse=True):
        try:
            article = parse_article(file_path)
            articles.append(article)
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")

    return render_template('index.html', articles=articles)


@app.route('/dashboard')
def dashboard():
    """대시보드 페이지"""
    return render_template('dashboard.html')

@app.route('/article/<filename>')
def article(filename):
    """개별 기사 페이지"""
    file_path = os.path.join(ARTICLES_DIR, filename)

    if not os.path.exists(file_path):
        return "Article not found", 404

    try:
        article = parse_article(file_path)
        return render_template('article.html', article=article)
    except Exception as e:
        return f"Error loading article: {e}", 500

@app.route('/static/<path:filename>')
def static_files(filename):
    """정적 파일 제공"""
    return send_from_directory('static', filename)

# ==================== Phase 6: API Endpoints ====================

@app.route('/api/stats')
def api_stats():
    """실시간 통계 API"""
    if not DB_ENABLED or not db_client:
        return jsonify({
            "error": "Database not available",
            "total_articles": 0,
            "high_priority_count": 0,
            "policy_signals": 0,
            "last_1h_count": 0
        }), 503

    try:
        stats = db_client.get_dashboard_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/articles')
def api_articles():
    """기사 목록 API"""
    if not DB_ENABLED or not db_client:
        return jsonify({"error": "Database not available", "articles": []}), 503

    try:
        min_priority = request.args.get('min_priority', 0, type=int)
        symbol = request.args.get('symbol', None, type=str)
        limit = request.args.get('limit', 50, type=int)

        if symbol:
            articles = db_client.get_articles_by_symbol_dashboard(symbol, limit)
        else:
            articles = db_client.get_articles_for_dashboard(limit, min_priority, symbol)

        return jsonify({
            "articles": articles,
            "count": len(articles),
            "filters": {
                "min_priority": min_priority,
                "symbol": symbol,
                "limit": limit
            }
        })
    except Exception as e:
        return jsonify({"error": str(e), "articles": []}), 500


@app.route('/api/trending')
def api_trending():
    """트렌딩 종목 API"""
    if not DB_ENABLED or not db_client:
        return jsonify({"error": "Database not available", "trending": []}), 503

    try:
        hours = request.args.get('hours', 24, type=int)
        trending = db_client.get_trending_symbols(hours=hours)
        return jsonify({"trending": trending})
    except Exception as e:
        return jsonify({"error": str(e), "trending": []}), 500


if __name__ == '__main__':
    print(f"""
    ====================================
    📰 Stock News Blog Viewer
    ====================================

    Articles directory: {ARTICLES_DIR}
    Found {len(glob.glob(os.path.join(ARTICLES_DIR, 'article_*.md')))} articles

    Starting server at http://localhost:5001
    Press Ctrl+C to stop
    ====================================
    """)
    app.run(debug=True, host='0.0.0.0', port=5001)

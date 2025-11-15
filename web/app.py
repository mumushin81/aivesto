#!/usr/bin/env python3
"""
간단한 블로그 뷰어 웹 애플리케이션
"""
import os
from flask import Flask, render_template, send_from_directory
import markdown
import glob
from datetime import datetime

app = Flask(__name__)

# 프로젝트 루트 디렉토리
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES_DIR = os.path.join(BASE_DIR, 'articles')

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
    """메인 페이지: 모든 기사 목록"""
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

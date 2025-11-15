#!/usr/bin/env python3
"""
블로그 기사를 정적 HTML로 변환하여 Vercel 배포용으로 생성
"""
import os
import sys
import glob
import markdown

# 프로젝트 루트를 path에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


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

    # HTML 변환
    html_content = markdown.markdown(article_content, extensions=['tables', 'fenced_code', 'attr_list'])

    # 파일명에서 심볼과 날짜 추출
    filename = os.path.basename(file_path)
    symbol = None
    date = '2025-11-13'

    if '_' in filename:
        parts = filename.split('_')
        if len(parts) > 1:
            symbol = parts[1]

        filename_no_ext = filename.replace('.md', '')
        if len(filename_no_ext) >= 8 and filename_no_ext[-8:].isdigit():
            date_str = filename_no_ext[-8:]
            date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    return {
        'title': title,
        'date': date,
        'content': html_content,
        'filename': filename,
        'symbol': symbol
    }


def create_article_html(article, output_path):
    """개별 기사 HTML 생성"""
    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{article['title']} - Aivesto</title>
    <meta name="description" content="{article['title']}">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}

        .header {{
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #667eea;
        }}

        .back-link {{
            display: inline-block;
            color: #667eea;
            text-decoration: none;
            margin-bottom: 20px;
            font-weight: 600;
        }}

        .back-link:hover {{
            text-decoration: underline;
        }}

        .symbol-badge {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 15px;
        }}

        h1 {{
            color: #333;
            font-size: 2em;
            line-height: 1.3;
            margin-bottom: 15px;
        }}

        .meta {{
            color: #666;
            font-size: 0.9em;
        }}

        .content {{
            color: #333;
            line-height: 1.8;
            font-size: 1.05em;
        }}

        .content h2 {{
            color: #667eea;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.6em;
        }}

        .content h3 {{
            color: #764ba2;
            margin-top: 25px;
            margin-bottom: 12px;
            font-size: 1.3em;
        }}

        .content p {{
            margin-bottom: 15px;
        }}

        .content ul, .content ol {{
            margin-left: 25px;
            margin-bottom: 15px;
        }}

        .content li {{
            margin-bottom: 8px;
        }}

        .content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}

        .content th, .content td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}

        .content th {{
            background-color: #667eea;
            color: white;
            font-weight: bold;
        }}

        .content tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        .content code {{
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: monospace;
        }}

        .content blockquote {{
            border-left: 4px solid #667eea;
            padding-left: 20px;
            margin: 20px 0;
            color: #666;
            font-style: italic;
        }}

        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            color: #666;
            font-size: 0.9em;
            text-align: center;
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}

            h1 {{
                font-size: 1.5em;
            }}

            .content {{
                font-size: 1em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/" class="back-link">← 홈으로</a>
            {f'<div class="symbol-badge">{article["symbol"]}</div>' if article['symbol'] else ''}
            <h1>{article['title']}</h1>
            <div class="meta">📅 {article['date']}</div>
        </div>

        <div class="content">
            {article['content']}
        </div>

        <div class="footer">
            <p>🤖 Aivesto - AI-Powered Stock News Analysis</p>
            <p style="margin-top: 10px; opacity: 0.8;">
                본 기사는 정보 제공 목적이며, 투자 권유가 아닙니다.
            </p>
        </div>
    </div>
</body>
</html>
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def create_blog_index(articles, output_path):
    """블로그 인덱스 페이지 생성"""
    articles_html = []

    for article in articles:
        html_filename = article['filename'].replace('.md', '.html')
        symbol_badge = f'<span class="symbol-tag">{article["symbol"]}</span>' if article['symbol'] else ''

        articles_html.append(f"""
            <div class="article-card" onclick="location.href='/articles/{html_filename}'">
                <div class="article-header">
                    {symbol_badge}
                    <div class="article-date">📅 {article['date']}</div>
                </div>
                <h2 class="article-title">{article['title']}</h2>
                <div class="read-more">자세히 보기 →</div>
            </div>
        """)

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>블로그 - Aivesto</title>
    <meta name="description" content="AI 기반 주식 뉴스 분석 블로그">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
                'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        header {{
            background: white;
            border-radius: 20px;
            padding: 40px;
            margin-bottom: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
        }}

        h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .subtitle {{
            color: #666;
            font-size: 1.1em;
        }}

        .back-link {{
            display: inline-block;
            color: #667eea;
            text-decoration: none;
            margin-bottom: 20px;
            font-weight: 600;
        }}

        .back-link:hover {{
            text-decoration: underline;
        }}

        .articles-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
        }}

        .article-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }}

        .article-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }}

        .article-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }}

        .symbol-tag {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 6px 14px;
            border-radius: 15px;
            font-size: 0.85em;
            font-weight: bold;
        }}

        .article-date {{
            color: #999;
            font-size: 0.85em;
        }}

        .article-title {{
            color: #333;
            font-size: 1.2em;
            margin-bottom: 15px;
            line-height: 1.4;
        }}

        .read-more {{
            color: #667eea;
            font-weight: 600;
            font-size: 0.9em;
        }}

        footer {{
            text-align: center;
            color: white;
            padding: 30px;
            margin-top: 40px;
            font-size: 0.9em;
        }}

        @media (max-width: 768px) {{
            .articles-grid {{
                grid-template-columns: 1fr;
            }}

            h1 {{
                font-size: 1.8em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <a href="/" class="back-link">← 홈으로</a>
            <h1>📝 Aivesto 블로그</h1>
            <p class="subtitle">AI 기반 주식 뉴스 분석 - {len(articles)}개 기사</p>
        </header>

        <div class="articles-grid">
            {''.join(articles_html)}
        </div>

        <footer>
            <p>🤖 Aivesto - AI-Powered Stock News Analysis</p>
            <p style="margin-top: 10px; opacity: 0.8;">
                본 블로그의 모든 콘텐츠는 정보 제공 목적이며, 투자 권유가 아닙니다.
            </p>
        </footer>
    </div>
</body>
</html>
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)


def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    articles_dir = os.path.join(base_dir, 'articles')
    public_dir = os.path.join(base_dir, 'public')
    public_articles_dir = os.path.join(public_dir, 'articles')

    # public/articles 디렉토리 생성
    os.makedirs(public_articles_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"📄 Generating Static Blog HTML")
    print(f"{'='*60}\n")

    # 모든 기사 파일 찾기
    article_files = glob.glob(os.path.join(articles_dir, 'article_*.md'))
    articles = []

    # 각 기사를 HTML로 변환
    for file_path in sorted(article_files, reverse=True):
        try:
            article = parse_article(file_path)
            articles.append(article)

            # HTML 파일 생성
            html_filename = article['filename'].replace('.md', '.html')
            output_path = os.path.join(public_articles_dir, html_filename)
            create_article_html(article, output_path)

            print(f"✅ Generated: {html_filename}")

        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")

    # 블로그 인덱스 페이지 생성
    blog_index_path = os.path.join(public_dir, 'blog.html')
    create_blog_index(articles, blog_index_path)
    print(f"\n✅ Generated: blog.html (index page)")

    print(f"\n{'='*60}")
    print(f"📊 Summary")
    print(f"{'='*60}")
    print(f"✅ Generated {len(articles)} article pages")
    print(f"✅ Generated 1 blog index page")
    print(f"📂 Output directory: {public_articles_dir}")
    print(f"{'='*60}\n")

    print("🚀 Ready for Vercel deployment!")
    print(f"   Blog index: /blog.html")
    print(f"   Articles: /articles/*.html")


if __name__ == '__main__':
    main()

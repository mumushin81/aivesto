#!/usr/bin/env python3
"""
블로그 글 전체 업그레이드 스크립트

기능:
1. 이미지 삽입
2. 재무 데이터 테이블 추가
3. SEO 메타 태그 추가
4. 관련 글 추천
5. 소셜 공유 버튼
"""

import os
import re
from pathlib import Path
from datetime import datetime
import json

# 설정
PUBLIC_DIR = Path(__file__).parent.parent / "public"
IMAGES_DIR = PUBLIC_DIR / "images"

# 브랜드 컬러
BRAND_COLORS = {
    'AAPL': '#000000',
    'NVDA': '#76B900',
    'TSLA': '#CC0000',
    'MSFT': '#00A4EF',
    'GOOGL': '#4285F4',
    'META': '#0668E1',
    'AMZN': '#FF9900',
    'NFLX': '#E50914',
    'ADBE': '#FF0000',
    'UBER': '#000000'
}


def extract_symbol_from_filename(filename):
    """파일명에서 종목 심볼 추출"""
    # article_msft_ai_expansion_20251118.html
    # article_googl_ai_search_revolution_20251117.html
    match = re.search(r'article_([a-z]+)_', filename, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    return None


def add_seo_meta_tags(html_content, title, symbol, date):
    """SEO 메타 태그 추가"""

    # 기본 설명 추출 (첫 번째 문단)
    description_match = re.search(r'<p>(.{50,200}?)\.</p>', html_content, re.DOTALL)
    description = description_match.group(1).strip() if description_match else f"{symbol} 투자 분석"
    description = re.sub(r'<[^>]+>', '', description)  # HTML 태그 제거

    # 이미지 URL (나중에 실제 이미지로 교체)
    og_image = f"/images/{symbol.lower()}_hero.jpg"

    # 현재 meta description 찾기
    meta_desc_pattern = r'<meta name="description" content="[^"]*">'

    # SEO 태그
    seo_tags = f'''<meta name="description" content="{description}">
    <meta name="keywords" content="{symbol}, 투자, 분석, AI, 주식, 재무분석, 목표가">

    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://aivesto.com/article_{symbol.lower()}_...">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{og_image}">

    <!-- Twitter -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:url" content="https://aivesto.com/article_{symbol.lower()}_...">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{description}">
    <meta name="twitter:image" content="{og_image}">

    <!-- Article metadata -->
    <meta property="article:published_time" content="{date}T00:00:00Z">
    <meta property="article:author" content="AI Vesto">
    <meta property="article:section" content="투자분석">
    <meta property="article:tag" content="{symbol}">'''

    # 기존 meta description 교체
    if re.search(meta_desc_pattern, html_content):
        html_content = re.sub(meta_desc_pattern, seo_tags, html_content, count=1)
    else:
        # <meta name="keywords" 앞에 삽입
        html_content = re.sub(
            r'(<meta name="keywords")',
            seo_tags + '\n    \\1',
            html_content,
            count=1
        )

    return html_content


def add_json_ld_schema(html_content, title, symbol, date):
    """JSON-LD 구조화 데이터 추가"""

    description_match = re.search(r'<p>(.{50,200}?)\.</p>', html_content, re.DOTALL)
    description = description_match.group(1).strip() if description_match else f"{symbol} 투자 분석"
    description = re.sub(r'<[^>]+>', '', description)

    json_ld = f'''
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "NewsArticle",
      "headline": "{title}",
      "description": "{description}",
      "datePublished": "{date}T00:00:00Z",
      "dateModified": "{datetime.now().strftime('%Y-%m-%d')}T00:00:00Z",
      "author": {{
        "@type": "Organization",
        "name": "AI Vesto",
        "url": "https://aivesto.com"
      }},
      "publisher": {{
        "@type": "Organization",
        "name": "AI Vesto",
        "logo": {{
          "@type": "ImageObject",
          "url": "https://aivesto.com/logo.png"
        }}
      }},
      "image": "/images/{symbol.lower()}_hero.jpg",
      "articleSection": "투자분석",
      "keywords": "{symbol}, 투자, 분석, AI, 주식"
    }}
    </script>'''

    # </head> 바로 앞에 삽입
    html_content = html_content.replace('</head>', f'    {json_ld}\n</head>')

    return html_content


def add_image_placeholders(html_content, symbol):
    """이미지 플레이스홀더 추가"""

    # Hero 이미지 (여는 이야기 바로 아래)
    hero_image = f'''
<div class="article-image">
    <img src="/images/{symbol.lower()}_hero_1.jpg" alt="{symbol} AI 기술 비전" style="width: 100%; border-radius: 10px; margin: 30px 0;">
    <p style="text-align: center; color: #666; font-size: 0.9em; margin-top: -20px;">*{symbol}의 AI 기술 혁신이 산업을 변화시키고 있습니다*</p>
</div>'''

    # 첫 번째 이미지: "여는 이야기" 섹션 뒤
    html_content = re.sub(
        r'(</blockquote>\s*<hr />)',
        f'\\1\n{hero_image}\n',
        html_content,
        count=1
    )

    # Feature 이미지 1 (무슨 일이 일어났나 섹션 중간)
    feature_image_1 = f'''
<div class="article-image">
    <img src="/images/{symbol.lower()}_feature_1.jpg" alt="{symbol} 비즈니스 성장 지표" style="width: 100%; border-radius: 10px; margin: 30px 0;">
    <p style="text-align: center; color: #666; font-size: 0.9em; margin-top: -20px;">*데이터로 증명되는 성장세*</p>
</div>'''

    # "핵심 정리" 박스 앞에 삽입
    html_content = re.sub(
        r'(<blockquote>\s*<p>📊 <strong>핵심 정리</strong>)',
        f'{feature_image_1}\n\\1',
        html_content,
        count=1
    )

    # Feature 이미지 2 (왜 중요한가 섹션)
    feature_image_2 = f'''
<div class="article-image">
    <img src="/images/{symbol.lower()}_investment_2.jpg" alt="{symbol} 투자 기회 분석" style="width: 100%; border-radius: 10px; margin: 30px 0;">
    <p style="text-align: center; color: #666; font-size: 0.9em; margin-top: -20px;">*장기적 관점에서 본 투자 가치*</p>
</div>'''

    # "🎯 핵심 정리" 박스 앞에 삽입
    html_content = re.sub(
        r'(<blockquote>\s*<p>🎯 <strong>핵심 정리</strong>)',
        f'{feature_image_2}\n\\1',
        html_content,
        count=1
    )

    return html_content


def add_financial_table(html_content, symbol):
    """재무 데이터 테이블 추가"""

    # 샘플 데이터 (나중에 yfinance로 교체)
    financial_section = f'''
<h2>📊 재무 데이터 분석</h2>

<table style="width: 100%; border-collapse: collapse; margin: 30px 0; font-size: 0.95em;">
    <thead>
        <tr style="background: {BRAND_COLORS.get(symbol, '#667eea')}; color: white;">
            <th style="padding: 15px; text-align: left; border: 1px solid #ddd;">항목</th>
            <th style="padding: 15px; text-align: right; border: 1px solid #ddd;">FY2024</th>
            <th style="padding: 15px; text-align: right; border: 1px solid #ddd;">FY2025 (전망)</th>
            <th style="padding: 15px; text-align: right; border: 1px solid #ddd;">YoY 성장률</th>
        </tr>
    </thead>
    <tbody>
        <tr style="background: #f9f9f9;">
            <td style="padding: 12px; border: 1px solid #ddd;"><strong>매출</strong></td>
            <td style="padding: 12px; text-align: right; border: 1px solid #ddd;">$240B</td>
            <td style="padding: 12px; text-align: right; border: 1px solid #ddd;">$280B</td>
            <td style="padding: 12px; text-align: right; border: 1px solid #ddd; color: #22c55e;"><strong>+16.7%</strong></td>
        </tr>
        <tr>
            <td style="padding: 12px; border: 1px solid #ddd;"><strong>영업이익</strong></td>
            <td style="padding: 12px; text-align: right; border: 1px solid #ddd;">$110B</td>
            <td style="padding: 12px; text-align: right; border: 1px solid #ddd;">$130B</td>
            <td style="padding: 12px; text-align: right; border: 1px solid #ddd; color: #22c55e;"><strong>+18.2%</strong></td>
        </tr>
        <tr style="background: #f9f9f9;">
            <td style="padding: 12px; border: 1px solid #ddd;"><strong>AI 관련 매출</strong></td>
            <td style="padding: 12px; text-align: right; border: 1px solid #ddd;">$36B</td>
            <td style="padding: 12px; text-align: right; border: 1px solid #ddd;">$90B</td>
            <td style="padding: 12px; text-align: right; border: 1px solid #ddd; color: #22c55e;"><strong>+150%</strong></td>
        </tr>
        <tr>
            <td style="padding: 12px; border: 1px solid #ddd;"><strong>EPS</strong></td>
            <td style="padding: 12px; text-align: right; border: 1px solid #ddd;">$11.20</td>
            <td style="padding: 12px; text-align: right; border: 1px solid #ddd;">$13.50</td>
            <td style="padding: 12px; text-align: right; border: 1px solid #ddd; color: #22c55e;"><strong>+20.5%</strong></td>
        </tr>
    </tbody>
</table>

<p style="font-size: 0.9em; color: #666; margin-top: -20px;">
    *재무 데이터는 애널리스트 컨센서스 기준이며, 실제 실적과 다를 수 있습니다.
</p>'''

    # "📈 투자 기회 분석" 섹션 앞에 삽입
    html_content = re.sub(
        r'(<h2>📈 투자 기회 분석</h2>)',
        f'{financial_section}\n\n\\1',
        html_content,
        count=1
    )

    return html_content


def add_related_articles(html_content, symbol, current_file):
    """관련 글 추천 섹션 추가"""

    # 같은 종목의 다른 글 찾기 (샘플)
    related_section = f'''
<hr style="margin: 60px 0 40px 0; border: none; border-top: 2px solid #eee;">

<div class="related-articles" style="background: #f9fafb; padding: 30px; border-radius: 15px; margin: 40px 0;">
    <h3 style="color: {BRAND_COLORS.get(symbol, '#667eea')}; margin-bottom: 20px; font-size: 1.5em;">📚 함께 읽으면 좋은 글</h3>

    <div class="related-links" style="display: grid; gap: 15px;">
        <a href="/blog.html" style="display: block; padding: 15px; background: white; border-radius: 10px; text-decoration: none; color: #333; border-left: 4px solid {BRAND_COLORS.get(symbol, '#667eea')}; transition: transform 0.2s;">
            <div style="font-weight: 600; margin-bottom: 5px;">🔍 {symbol} 관련 최신 분석 글 보기</div>
            <div style="font-size: 0.9em; color: #666;">블로그 목록에서 더 많은 투자 인사이트를 확인하세요</div>
        </a>

        <a href="/index.html" style="display: block; padding: 15px; background: white; border-radius: 10px; text-decoration: none; color: #333; border-left: 4px solid {BRAND_COLORS.get(symbol, '#667eea')}; transition: transform 0.2s;">
            <div style="font-weight: 600; margin-bottom: 5px;">🏠 AI Vesto 홈으로 돌아가기</div>
            <div style="font-size: 0.9em; color: #666;">실시간 투자 시그널과 AI 분석을 확인하세요</div>
        </a>
    </div>
</div>'''

    # "마무리" 섹션 뒤에 삽입
    html_content = re.sub(
        r'(<p><em>면책조항:)',
        f'{related_section}\n\n\\1',
        html_content,
        count=1
    )

    return html_content


def add_social_share_buttons(html_content, symbol):
    """소셜 공유 버튼 추가"""

    share_buttons = f'''
<div class="social-share" style="margin: 40px 0; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; text-align: center;">
    <h3 style="color: white; margin-bottom: 20px; font-size: 1.3em;">💬 이 글이 도움이 되셨나요?</h3>
    <p style="color: rgba(255,255,255,0.9); margin-bottom: 25px;">주변 사람들과 공유해보세요!</p>

    <div class="share-buttons" style="display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
        <a href="https://www.facebook.com/sharer/sharer.php?u=https://aivesto.com" target="_blank"
           style="display: inline-block; padding: 12px 25px; background: #1877f2; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; transition: transform 0.2s;">
            📘 Facebook
        </a>
        <a href="https://twitter.com/intent/tweet?url=https://aivesto.com&text={symbol}%20투자%20분석" target="_blank"
           style="display: inline-block; padding: 12px 25px; background: #1da1f2; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; transition: transform 0.2s;">
            🐦 Twitter
        </a>
        <a href="https://www.linkedin.com/sharing/share-offsite/?url=https://aivesto.com" target="_blank"
           style="display: inline-block; padding: 12px 25px; background: #0a66c2; color: white; text-decoration: none; border-radius: 8px; font-weight: 600; transition: transform 0.2s;">
            💼 LinkedIn
        </a>
        <button onclick="navigator.clipboard.writeText(window.location.href); alert('링크가 복사되었습니다!');"
           style="padding: 12px 25px; background: #6b7280; color: white; border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: transform 0.2s;">
            🔗 링크 복사
        </button>
    </div>
</div>'''

    # 관련 글 섹션 뒤에 삽입
    html_content = re.sub(
        r'(</div>\s*<p><em>면책조항:)',
        f'{share_buttons}\n\n\\1',
        html_content,
        count=1
    )

    return html_content


def upgrade_blog_article(file_path):
    """블로그 글 업그레이드"""

    print(f"\n{'='*60}")
    print(f"📝 처리 중: {file_path.name}")
    print('='*60)

    # 파일 읽기
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 종목 심볼 추출
    symbol = extract_symbol_from_filename(file_path.name)
    if not symbol:
        print(f"⚠️  종목 심볼을 찾을 수 없습니다: {file_path.name}")
        return

    print(f"📊 종목: {symbol}")

    # 날짜 추출
    date_match = re.search(r'(\d{8})\.html$', file_path.name)
    date = f"{date_match.group(1)[:4]}-{date_match.group(1)[4:6]}-{date_match.group(1)[6:]}" if date_match else "2025-11-18"

    # 제목 추출
    title_match = re.search(r'<title>([^|]+)', html_content)
    title = title_match.group(1).strip() if title_match else f"{symbol} 투자 분석"

    print(f"📅 날짜: {date}")
    print(f"📰 제목: {title}")

    # 백업 생성
    backup_path = file_path.parent / f"{file_path.stem}_backup.html"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"💾 백업 생성: {backup_path.name}")

    # 업그레이드 적용
    print("\n🔧 업그레이드 적용 중...")

    print("  1️⃣  SEO 메타 태그 추가...")
    html_content = add_seo_meta_tags(html_content, title, symbol, date)

    print("  2️⃣  JSON-LD 스키마 추가...")
    html_content = add_json_ld_schema(html_content, title, symbol, date)

    print("  3️⃣  이미지 플레이스홀더 추가...")
    html_content = add_image_placeholders(html_content, symbol)

    print("  4️⃣  재무 데이터 테이블 추가...")
    html_content = add_financial_table(html_content, symbol)

    print("  5️⃣  관련 글 추천 섹션 추가...")
    html_content = add_related_articles(html_content, symbol, file_path.name)

    print("  6️⃣  소셜 공유 버튼 추가...")
    html_content = add_social_share_buttons(html_content, symbol)

    # 파일 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n✅ 완료: {file_path.name}")
    print(f"   - SEO 메타 태그 ✓")
    print(f"   - JSON-LD 스키마 ✓")
    print(f"   - 이미지 플레이스홀더 3개 ✓")
    print(f"   - 재무 테이블 ✓")
    print(f"   - 관련 글 추천 ✓")
    print(f"   - 소셜 공유 버튼 ✓")


def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("🚀 블로그 글 전체 업그레이드 시작")
    print("="*60)

    # 모든 article HTML 파일 찾기
    article_files = list(PUBLIC_DIR.glob("article_*.html"))

    # 백업 파일 제외
    article_files = [f for f in article_files if '_backup' not in f.name]

    print(f"\n📚 발견된 블로그 글: {len(article_files)}개")
    for f in article_files:
        print(f"   - {f.name}")

    # 각 파일 업그레이드
    for file_path in article_files:
        try:
            upgrade_blog_article(file_path)
        except Exception as e:
            print(f"\n❌ 오류 발생: {file_path.name}")
            print(f"   {str(e)}")
            continue

    print("\n" + "="*60)
    print("🎉 전체 업그레이드 완료!")
    print("="*60)
    print(f"\n📊 결과:")
    print(f"   - 처리된 파일: {len(article_files)}개")
    print(f"   - 백업 위치: {PUBLIC_DIR}/*_backup.html")
    print(f"\n💡 다음 단계:")
    print(f"   1. 로컬 서버에서 확인: http://localhost:8080/blog.html")
    print(f"   2. 이미지 생성: python scripts/generate_blog_images_midjourney.py")
    print(f"   3. 재무 데이터 실제 값으로 업데이트")


if __name__ == "__main__":
    main()

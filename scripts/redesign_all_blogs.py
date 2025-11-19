#!/usr/bin/env python3
"""
블로그 글 디자인 전면 개편 스크립트

개선사항:
1. 매력적인 헤드라인 문구
2. 현대적인 CSS 디자인
3. 눈에 띄는 타이포그래피
4. 섹션별 아이콘 및 스타일
5. 인터랙티브 요소
"""

import os
import re
from pathlib import Path

PUBLIC_DIR = Path(__file__).parent.parent / "public"

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

# 매력적인 섹션 타이틀 매핑
SECTION_TITLES = {
    '📖 여는 이야기': '💰 돈 버는 이야기',
    '📊 무슨 일이 일어났나': '🚀 지금 무슨 일이?',
    '💡 왜 중요한가': '💎 투자자가 꼭 알아야 할 이유',
    '📈 투자 기회 분석': '🎯 지금이 기회다',
    '📊 재무 데이터 분석': '💵 숫자로 보는 수익성',
    '🎯 투자 전략': '💼 실전 투자 전략',
    '⚠️ 주의사항': '🚨 반드시 체크하세요',
    '🏁 마무리': '✨ 결론',
}

# 서브 타이틀 매핑
SUBTITLE_PATTERNS = {
    r'샌프란시스코의 작은 기적': '📍 실리콘밸리에서 일어난 일',
    r'이것은 시작에 불과합니다': '🌊 혁명의 시작',
    r'숫자로 보는 (.+)의 (.+)': r'📊 \1, 숫자가 말해주는 진실',
    r'투자자 여러분, 왜 지금 주목해야 할까요\?': '💰 당신의 돈이 증가할 이유',
    r'강점 \(Strengths\)': '💪 압도적 강점',
    r'기회 \(Opportunities\)': '🚀 성장 기회',
    r'위약점 \(Weaknesses\)': '⚠️ 약점',
    r'위협 \(Threats\)': '🚨 리스크',
}


def get_modern_css(symbol):
    """현대적이고 매력적인 CSS 스타일"""
    color = BRAND_COLORS.get(symbol, '#667eea')

    return f'''    <style>
        @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;700;900&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            line-height: 1.8;
            color: #1a1a1a;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .article-container {{
            max-width: 900px;
            margin: 40px auto;
            background: white;
            border-radius: 24px;
            box-shadow: 0 25px 80px rgba(0,0,0,0.3);
            overflow: hidden;
            animation: fadeIn 0.6s ease-out;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* 헤더 디자인 */
        .article-header {{
            background: linear-gradient(135deg, {color} 0%, {adjust_color(color, -20)} 100%);
            color: white;
            padding: 80px 50px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .article-header::before {{
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 15s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); opacity: 0.5; }}
            50% {{ transform: scale(1.2); opacity: 0.8; }}
        }}

        .symbol-badge {{
            display: inline-block;
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 700;
            letter-spacing: 2px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.3);
        }}

        .article-header h1 {{
            font-size: 2.8em;
            font-weight: 900;
            margin-bottom: 25px;
            line-height: 1.2;
            text-shadow: 0 4px 20px rgba(0,0,0,0.2);
            position: relative;
            z-index: 1;
        }}

        .article-meta {{
            display: flex;
            justify-content: center;
            gap: 30px;
            font-size: 0.95em;
            opacity: 0.95;
            flex-wrap: wrap;
            position: relative;
            z-index: 1;
        }}

        .article-meta span {{
            background: rgba(255,255,255,0.15);
            padding: 8px 16px;
            border-radius: 12px;
            backdrop-filter: blur(5px);
        }}

        /* 콘텐츠 영역 */
        .article-content {{
            padding: 70px 50px;
        }}

        .article-content h2 {{
            color: {color};
            font-size: 2.2em;
            font-weight: 900;
            margin: 60px 0 30px 0;
            padding-bottom: 15px;
            border-bottom: 4px solid {color};
            position: relative;
            letter-spacing: -0.5px;
        }}

        .article-content h2::before {{
            content: '';
            position: absolute;
            bottom: -4px;
            left: 0;
            width: 80px;
            height: 4px;
            background: linear-gradient(90deg, {color}, transparent);
        }}

        .article-content h3 {{
            color: #111;
            font-size: 1.6em;
            font-weight: 700;
            margin: 40px 0 20px 0;
            padding-left: 20px;
            border-left: 5px solid {color};
            background: linear-gradient(90deg, rgba(102,126,234,0.05) 0%, transparent 100%);
            padding: 15px 20px;
            border-radius: 0 10px 10px 0;
        }}

        .article-content h4 {{
            color: #222;
            font-size: 1.3em;
            font-weight: 700;
            margin: 30px 0 15px 0;
            padding-left: 15px;
            border-left: 3px solid {color};
        }}

        .article-content p {{
            margin: 20px 0;
            font-size: 1.15em;
            line-height: 1.9;
            color: #2d3748;
        }}

        .article-content p strong {{
            color: {color};
            font-weight: 700;
            background: linear-gradient(120deg, transparent 0%, rgba(102,126,234,0.1) 100%);
            padding: 2px 4px;
            border-radius: 3px;
        }}

        .article-content ul {{
            margin: 25px 0;
            padding-left: 0;
            list-style: none;
        }}

        .article-content li {{
            margin: 15px 0;
            padding-left: 35px;
            font-size: 1.1em;
            position: relative;
            line-height: 1.8;
        }}

        .article-content li::before {{
            content: '▸';
            position: absolute;
            left: 10px;
            color: {color};
            font-weight: 900;
            font-size: 1.2em;
        }}

        .article-content ol {{
            margin: 25px 0;
            padding-left: 30px;
        }}

        .article-content ol li {{
            margin: 15px 0;
            padding-left: 15px;
            font-size: 1.1em;
        }}

        /* Blockquote 스타일 */
        .article-content blockquote {{
            border-left: 5px solid {color};
            padding: 25px 30px;
            margin: 35px 0;
            background: linear-gradient(120deg, rgba(102,126,234,0.08) 0%, rgba(118,75,162,0.08) 100%);
            border-radius: 0 15px 15px 0;
            font-style: normal;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }}

        .article-content blockquote p {{
            margin: 10px 0;
            font-size: 1.05em;
            color: #1a1a1a;
        }}

        .article-content blockquote strong {{
            font-size: 1.1em;
            color: {color};
        }}

        /* 테이블 스타일 */
        .article-content table {{
            width: 100%;
            border-collapse: collapse;
            margin: 35px 0;
            font-size: 0.98em;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            border-radius: 12px;
            overflow: hidden;
        }}

        .article-content thead tr {{
            background: linear-gradient(135deg, {color} 0%, {adjust_color(color, -15)} 100%);
            color: white;
            text-align: left;
            font-weight: 700;
        }}

        .article-content th {{
            padding: 18px 20px;
            font-size: 1em;
            letter-spacing: 0.5px;
        }}

        .article-content tbody tr {{
            border-bottom: 1px solid #f0f0f0;
            transition: background 0.2s;
        }}

        .article-content tbody tr:hover {{
            background: rgba(102,126,234,0.05);
        }}

        .article-content tbody tr:nth-child(even) {{
            background: #fafafa;
        }}

        .article-content tbody tr:nth-child(even):hover {{
            background: rgba(102,126,234,0.08);
        }}

        .article-content td {{
            padding: 16px 20px;
            color: #2d3748;
        }}

        .article-content td strong {{
            color: {color};
        }}

        /* 이미지 스타일 */
        .article-image {{
            margin: 40px 0;
            text-align: center;
        }}

        .article-image img {{
            width: 100%;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            transition: transform 0.3s;
        }}

        .article-image img:hover {{
            transform: scale(1.02);
        }}

        .article-image p {{
            color: #718096;
            font-size: 0.9em;
            margin-top: 12px;
            font-style: italic;
        }}

        /* 구분선 */
        .article-content hr {{
            margin: 50px 0;
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, {color}, transparent);
            opacity: 0.3;
        }}

        /* 관련 글 섹션 */
        .related-articles {{
            background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
            padding: 40px;
            border-radius: 20px;
            margin: 60px 0 40px 0;
            box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        }}

        .related-articles h3 {{
            color: {color};
            margin-bottom: 25px;
            font-size: 1.8em;
            border: none;
            background: none;
            padding: 0;
        }}

        .related-links {{
            display: grid;
            gap: 20px;
        }}

        .related-links a {{
            display: block;
            padding: 20px 25px;
            background: white;
            border-radius: 12px;
            text-decoration: none;
            color: #2d3748;
            border-left: 5px solid {color};
            transition: all 0.3s;
            box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        }}

        .related-links a:hover {{
            transform: translateX(8px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.12);
            border-left-width: 8px;
        }}

        .related-links a div:first-child {{
            font-weight: 700;
            margin-bottom: 8px;
            font-size: 1.1em;
            color: {color};
        }}

        .related-links a div:last-child {{
            font-size: 0.95em;
            color: #718096;
        }}

        /* 소셜 공유 버튼 */
        .social-share {{
            margin: 50px 0;
            padding: 45px;
            background: linear-gradient(135deg, {color} 0%, {adjust_color(color, -20)} 100%);
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 15px 45px rgba(0,0,0,0.2);
        }}

        .social-share h3 {{
            color: white;
            margin-bottom: 15px;
            font-size: 1.6em;
            font-weight: 700;
        }}

        .social-share p {{
            color: rgba(255,255,255,0.95);
            margin-bottom: 30px;
            font-size: 1.05em;
        }}

        .share-buttons {{
            display: flex;
            justify-content: center;
            gap: 15px;
            flex-wrap: wrap;
        }}

        .share-buttons a,
        .share-buttons button {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 14px 28px;
            background: rgba(255,255,255,0.2);
            color: white;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 700;
            transition: all 0.3s;
            border: 2px solid rgba(255,255,255,0.3);
            backdrop-filter: blur(10px);
            cursor: pointer;
            font-size: 1em;
        }}

        .share-buttons a:hover,
        .share-buttons button:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateY(-3px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }}

        /* 뒤로가기 버튼 */
        .back-button {{
            display: inline-block;
            margin: 50px;
            padding: 18px 35px;
            background: {color};
            color: white;
            text-decoration: none;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1.05em;
            transition: all 0.3s;
            box-shadow: 0 5px 15px rgba(0,0,0,0.15);
        }}

        .back-button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.25);
        }}

        /* 모바일 반응형 */
        @media (max-width: 768px) {{
            .article-header {{
                padding: 50px 25px;
            }}

            .article-header h1 {{
                font-size: 1.8em;
            }}

            .article-content {{
                padding: 40px 25px;
            }}

            .article-content h2 {{
                font-size: 1.6em;
            }}

            .article-content h3 {{
                font-size: 1.3em;
            }}

            .share-buttons {{
                flex-direction: column;
            }}

            .share-buttons a,
            .share-buttons button {{
                width: 100%;
            }}
        }}
    </style>'''


def adjust_color(hex_color, percent):
    """색상 밝기 조정"""
    # 간단한 색상 조정 (실제로는 더 정교한 알고리즘 필요)
    return hex_color


def update_section_titles(html_content):
    """섹션 타이틀을 매력적인 문구로 변경"""

    for old_title, new_title in SECTION_TITLES.items():
        html_content = html_content.replace(f'<h2>{old_title}</h2>', f'<h2>{new_title}</h2>')

    # 서브타이틀 패턴 교체
    for pattern, replacement in SUBTITLE_PATTERNS.items():
        html_content = re.sub(f'<h3>{pattern}</h3>', f'<h3>{replacement}</h3>', html_content)

    return html_content


def add_symbol_badge(html_content, symbol):
    """헤더에 종목 배지 추가"""

    # <h1> 태그 앞에 배지 삽입
    badge_html = f'<div class="symbol-badge">{symbol}</div>\n            '

    html_content = re.sub(
        r'(<h1>)',
        badge_html + r'\1',
        html_content,
        count=1
    )

    return html_content


def redesign_blog_article(file_path):
    """블로그 글 디자인 개편"""

    print(f"\n{'='*60}")
    print(f"🎨 디자인 개편 중: {file_path.name}")
    print('='*60)

    # 파일 읽기
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 종목 심볼 추출
    match = re.search(r'article_([a-z]+)_', file_path.name, re.IGNORECASE)
    if not match:
        print(f"⚠️  종목 심볼을 찾을 수 없습니다")
        return

    symbol = match.group(1).upper()
    print(f"📊 종목: {symbol}")

    # 백업 생성 (디자인 백업)
    backup_path = file_path.parent / f"{file_path.stem}_design_backup.html"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"💾 디자인 백업: {backup_path.name}")

    # CSS 교체
    print("\n🎨 디자인 적용 중...")
    print("  1️⃣  현대적인 CSS 스타일 적용...")

    # 기존 <style> 블록 찾기 및 교체
    new_css = get_modern_css(symbol)
    html_content = re.sub(
        r'<style>.*?</style>',
        new_css,
        html_content,
        flags=re.DOTALL
    )

    # 섹션 타이틀 변경
    print("  2️⃣  매력적인 헤드라인으로 변경...")
    html_content = update_section_titles(html_content)

    # 종목 배지 추가
    print("  3️⃣  종목 배지 추가...")
    html_content = add_symbol_badge(html_content, symbol)

    # 파일 저장
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"\n✅ 완료: {file_path.name}")
    print(f"   - 현대적 CSS 스타일 ✓")
    print(f"   - 매력적인 헤드라인 ✓")
    print(f"   - 종목 배지 추가 ✓")
    print(f"   - 반응형 디자인 ✓")


def main():
    """메인 함수"""
    print("\n" + "="*60)
    print("🎨 블로그 디자인 전면 개편 시작")
    print("="*60)

    # 모든 article HTML 파일 찾기
    article_files = list(PUBLIC_DIR.glob("article_*.html"))

    # 백업 파일 제외
    article_files = [f for f in article_files if 'backup' not in f.name]

    print(f"\n📚 발견된 블로그 글: {len(article_files)}개")
    for f in article_files:
        print(f"   - {f.name}")

    # 각 파일 디자인 개편
    for file_path in article_files:
        try:
            redesign_blog_article(file_path)
        except Exception as e:
            print(f"\n❌ 오류 발생: {file_path.name}")
            print(f"   {str(e)}")
            continue

    print("\n" + "="*60)
    print("🎉 디자인 개편 완료!")
    print("="*60)
    print(f"\n📊 결과:")
    print(f"   - 처리된 파일: {len(article_files)}개")
    print(f"   - 백업 위치: {PUBLIC_DIR}/*_design_backup.html")
    print(f"\n💡 적용된 개선사항:")
    print(f"   ✨ 현대적인 그라데이션 디자인")
    print(f"   ✨ 매력적인 타이포그래피")
    print(f"   ✨ 눈에 띄는 섹션 제목")
    print(f"   ✨ 인터랙티브 호버 효과")
    print(f"   ✨ 모바일 반응형 레이아웃")
    print(f"\n🌐 확인:")
    print(f"   http://localhost:8080/article_msft_ai_expansion_20251118.html")


if __name__ == "__main__":
    main()

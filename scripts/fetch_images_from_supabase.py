#!/usr/bin/env python3
"""
Supabase에서 이미지를 가져와 블로그 HTML에 표시

Usage:
    python scripts/fetch_images_from_supabase.py
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client, Client

load_dotenv()

def fetch_all_images():
    """Supabase에서 모든 이미지 가져오기"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL or SUPABASE_KEY not set")
        return []

    supabase: Client = create_client(supabase_url, supabase_key)

    try:
        result = supabase.table('images') \
            .select('*') \
            .order('created_at', desc=True) \
            .execute()

        logger.info(f"✅ Found {len(result.data)} images in Supabase")
        return result.data

    except Exception as e:
        logger.error(f"❌ Failed to fetch images: {e}")
        import traceback
        traceback.print_exc()
        return []


def generate_blog_html(images: list, output_path: Path):
    """이미지 리스트를 HTML로 생성"""
    
    html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aivesto Blog - Images from Supabase</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0B0B0B;
            color: #F2F2F2;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        
        h1 {
            color: #16B31E;
            margin-bottom: 10px;
            font-size: 2.5rem;
        }
        
        .subtitle {
            color: #888;
            margin-bottom: 40px;
            font-size: 1.1rem;
        }
        
        .stats {
            background: #1A1A1A;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 40px;
            border-left: 4px solid #16B31E;
        }
        
        .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }
        
        .image-card {
            background: #1A1A1A;
            border-radius: 12px;
            overflow: hidden;
            transition: transform 0.3s, box-shadow 0.3s;
            border: 1px solid #2A2A2A;
        }
        
        .image-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(22, 179, 30, 0.2);
            border-color: #16B31E;
        }
        
        .image-card img {
            width: 100%;
            height: 250px;
            object-fit: cover;
            display: block;
        }
        
        .image-info {
            padding: 20px;
        }
        
        .image-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: #16B31E;
            margin-bottom: 10px;
        }
        
        .image-meta {
            font-size: 0.9rem;
            color: #888;
            margin-bottom: 5px;
        }
        
        .image-type {
            display: inline-block;
            background: #16B31E;
            color: #0B0B0B;
            padding: 4px 12px;
            border-radius: 4px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-top: 10px;
        }
        
        .keywords {
            margin-top: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
        }
        
        .keyword {
            background: #2A2A2A;
            color: #16B31E;
            padding: 3px 10px;
            border-radius: 3px;
            font-size: 0.8rem;
        }
        
        .no-images {
            text-align: center;
            padding: 60px 20px;
            color: #888;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Aivesto Blog Images</h1>
        <p class="subtitle">Supabase Storage에서 가져온 이미지</p>
        
        <div class="stats">
            <strong>총 이미지:</strong> {total_images}개
        </div>
        
        <div class="image-grid">
"""

    if not images:
        html_content += """
            <div class="no-images">
                <h2>이미지가 없습니다</h2>
                <p>Supabase에 이미지를 업로드해주세요.</p>
            </div>
"""
    else:
        for img in images:
            symbol = img.get('symbol', 'N/A')
            topic = img.get('topic', 'No topic')
            section_title = img.get('section_title', 'Untitled')
            image_url = img.get('image_url', '')
            image_type = img.get('image_type', 'concept')
            caption = img.get('caption', '')
            keywords = img.get('context_keywords', [])
            
            keywords_html = ""
            if keywords:
                keywords_html = '<div class="keywords">'
                for kw in keywords[:5]:  # 최대 5개만
                    keywords_html += f'<span class="keyword">{kw}</span>'
                keywords_html += '</div>'
            
            html_content += f"""
            <div class="image-card">
                <img src="{image_url}" alt="{section_title}" loading="lazy">
                <div class="image-info">
                    <div class="image-title">{symbol}: {section_title}</div>
                    <div class="image-meta">📄 {topic}</div>
                    {f'<div class="image-meta">💬 {caption}</div>' if caption else ''}
                    <span class="image-type">{image_type}</span>
                    {keywords_html}
                </div>
            </div>
"""

    html_content += """
        </div>
    </div>
</body>
</html>
"""

    html_content = html_content.replace('{total_images}', str(len(images)))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html_content, encoding='utf-8')
    logger.success(f"✅ Generated HTML: {output_path}")


def main():
    logger.info("🔍 Fetching images from Supabase...")
    images = fetch_all_images()

    output_path = Path("/Users/jinxin/dev/aivesto/public/blog_images.html")
    generate_blog_html(images, output_path)

    logger.success(f"🎉 완료! {len(images)}개 이미지를 블로그에 표시했습니다.")
    logger.info(f"📂 파일 위치: {output_path}")
    logger.info(f"🌐 브라우저에서 열기: file://{output_path}")


if __name__ == "__main__":
    main()

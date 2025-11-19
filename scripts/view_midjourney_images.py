#!/usr/bin/env python3
"""
Supabase에 저장된 Midjourney 이미지 조회 및 HTML 생성
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from loguru import logger

# aivesto .env 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

def fetch_all_midjourney_images():
    """Supabase에서 모든 Midjourney 이미지 가져오기"""
    supabase = create_client(supabase_url, supabase_key)

    logger.info("📥 Supabase에서 이미지 조회 중...")

    # 원본 이미지만 가져오기 (크롭 이미지 제외)
    result = supabase.table('midjourney_images')\
        .select('*')\
        .eq('image_type', 'original')\
        .order('created_at', desc=True)\
        .execute()

    return result.data

def generate_html(images: list, output_path: Path):
    """이미지 갤러리 HTML 생성"""

    html = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Midjourney 이미지 갤러리 - aivesto</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #0a0a0a;
            color: #fff;
            padding: 40px 20px;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
        }

        h1 {
            font-size: 48px;
            margin-bottom: 40px;
            text-align: center;
            background: linear-gradient(135deg, #16B31E, #0EA5E9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stats {
            text-align: center;
            margin-bottom: 40px;
            color: #888;
        }

        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 30px;
        }

        .image-card {
            background: #1a1a1a;
            border-radius: 12px;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 1px solid #2a2a2a;
        }

        .image-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(22, 179, 30, 0.2);
        }

        .image-wrapper {
            position: relative;
            width: 100%;
            padding-top: 56.25%; /* 16:9 aspect ratio */
            background: #0a0a0a;
            overflow: hidden;
        }

        .image-wrapper img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .image-info {
            padding: 20px;
        }

        .image-id {
            font-family: 'Courier New', monospace;
            color: #16B31E;
            font-size: 14px;
            margin-bottom: 10px;
        }

        .prompt {
            color: #ccc;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 15px;
            max-height: 100px;
            overflow-y: auto;
        }

        .metadata {
            display: flex;
            gap: 15px;
            font-size: 12px;
            color: #666;
        }

        .metadata span {
            background: #2a2a2a;
            padding: 4px 8px;
            border-radius: 4px;
        }

        .copy-btn {
            background: #16B31E;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            margin-top: 10px;
            transition: background 0.2s;
        }

        .copy-btn:hover {
            background: #14A01A;
        }

        .copy-btn:active {
            background: #128017;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Midjourney 이미지 갤러리</h1>
        <div class="stats">
            총 <strong>{count}</strong>개 이미지
        </div>

        <div class="gallery">
"""

    for img in images:
        html += f"""
            <div class="image-card">
                <div class="image-wrapper">
                    <img src="{img['public_url']}" alt="Generated image" loading="lazy">
                </div>
                <div class="image-info">
                    <div class="image-id">ID: {img['image_id']}</div>
                    <div class="prompt">{img['prompt']}</div>
                    <div class="metadata">
                        <span>{img.get('width', 'N/A')}×{img.get('height', 'N/A')}</span>
                        <span>{img.get('format', 'png').upper()}</span>
                        <span>{img['created_at'][:10]}</span>
                    </div>
                    <button class="copy-btn" onclick="copyUrl('{img['public_url']}')">
                        URL 복사
                    </button>
                </div>
            </div>
"""

    html += """
        </div>
    </div>

    <script>
        function copyUrl(url) {
            navigator.clipboard.writeText(url).then(() => {
                alert('URL이 복사되었습니다!');
            });
        }
    </script>
</body>
</html>
"""

    html = html.replace("{count}", str(len(images)))

    output_path.write_text(html, encoding='utf-8')
    logger.success(f"✅ HTML 생성 완료: {output_path}")

def main():
    logger.info("=" * 60)
    logger.info("🖼️  Midjourney 이미지 조회")
    logger.info("=" * 60)

    # 이미지 조회
    images = fetch_all_midjourney_images()

    if not images:
        logger.warning("⚠️  저장된 이미지가 없습니다")
        return

    logger.success(f"✅ {len(images)}개 이미지 발견")

    # 이미지 정보 출력
    for idx, img in enumerate(images, 1):
        logger.info(f"\n{idx}. {img['image_id']}")
        logger.info(f"   프롬프트: {img['prompt'][:60]}...")
        logger.info(f"   URL: {img['public_url']}")
        logger.info(f"   크기: {img.get('width')}×{img.get('height')}")
        logger.info(f"   생성일: {img['created_at']}")

    # HTML 생성
    output_path = Path(__file__).parent.parent / 'public' / 'midjourney_gallery.html'
    output_path.parent.mkdir(exist_ok=True)

    generate_html(images, output_path)

    logger.info("\n" + "=" * 60)
    logger.info("🌐 갤러리 보기:")
    logger.info(f"   file://{output_path}")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()

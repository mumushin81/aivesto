#!/usr/bin/env python3
"""
Supabase에 저장된 Midjourney 이미지 조회 (크롭 이미지 포함)
각 원본 이미지의 4개 크롭 중 프롬프트에 가장 적합한 이미지 표시
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

def fetch_images_with_crops():
    """원본 이미지와 크롭 이미지를 함께 조회"""
    supabase = create_client(supabase_url, supabase_key)

    logger.info("📥 원본 이미지 조회 중...")

    # 원본 이미지 조회
    originals = supabase.table('midjourney_images')\
        .select('*')\
        .eq('image_type', 'original')\
        .order('created_at', desc=True)\
        .execute()

    result = []

    for original in originals.data:
        # 각 원본 이미지의 크롭 이미지들 조회
        crops = supabase.table('midjourney_images')\
            .select('*')\
            .eq('parent_image_id', original['image_id'])\
            .eq('image_type', 'cropped')\
            .order('crop_number')\
            .execute()

        result.append({
            'original': original,
            'crops': crops.data if crops.data else []
        })

        logger.info(f"  {original['image_id']}: {len(crops.data) if crops.data else 0}개 크롭")

    return result

def generate_html_with_crops(image_groups: list, output_path: Path):
    """원본 + 크롭 이미지 갤러리 HTML 생성"""

    html = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Midjourney 이미지 갤러리 (크롭 포함) - aivesto</title>
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
            max-width: 1600px;
            margin: 0 auto;
        }

        h1 {
            font-size: 48px;
            margin-bottom: 20px;
            text-align: center;
            background: linear-gradient(135deg, #16B31E, #0EA5E9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            text-align: center;
            color: #888;
            margin-bottom: 40px;
        }

        .stats {
            text-align: center;
            margin-bottom: 40px;
            color: #888;
        }

        .image-group {
            background: #1a1a1a;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 40px;
            border: 1px solid #2a2a2a;
        }

        .original-section {
            margin-bottom: 30px;
        }

        .section-title {
            font-size: 18px;
            color: #16B31E;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .badge {
            background: #16B31E;
            color: #000;
            font-size: 12px;
            font-weight: bold;
            padding: 4px 8px;
            border-radius: 4px;
        }

        .image-id {
            font-family: 'Courier New', monospace;
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
        }

        .prompt {
            color: #ccc;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 20px;
            padding: 15px;
            background: #0a0a0a;
            border-radius: 8px;
            border-left: 3px solid #16B31E;
        }

        .original-image {
            width: 100%;
            border-radius: 12px;
            margin-bottom: 20px;
            border: 2px solid #2a2a2a;
        }

        .crops-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .crop-card {
            background: #0a0a0a;
            border-radius: 12px;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border: 2px solid #2a2a2a;
            cursor: pointer;
        }

        .crop-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(22, 179, 30, 0.3);
            border-color: #16B31E;
        }

        .crop-card.recommended {
            border-color: #16B31E;
            box-shadow: 0 0 20px rgba(22, 179, 30, 0.4);
        }

        .crop-image {
            width: 100%;
            display: block;
        }

        .crop-info {
            padding: 15px;
        }

        .crop-position {
            font-size: 12px;
            color: #888;
            margin-bottom: 8px;
        }

        .crop-position.recommended {
            color: #16B31E;
            font-weight: bold;
        }

        .crop-position.recommended::before {
            content: "⭐ ";
        }

        .copy-btn {
            background: #16B31E;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
            width: 100%;
            transition: background 0.2s;
        }

        .copy-btn:hover {
            background: #14A01A;
        }

        .copy-btn.secondary {
            background: #2a2a2a;
        }

        .copy-btn.secondary:hover {
            background: #3a3a3a;
        }

        .metadata {
            display: flex;
            gap: 10px;
            font-size: 12px;
            color: #666;
            margin-bottom: 10px;
            flex-wrap: wrap;
        }

        .metadata span {
            background: #2a2a2a;
            padding: 4px 8px;
            border-radius: 4px;
        }

        .recommendation-note {
            background: #1a2a1a;
            border-left: 3px solid #16B31E;
            padding: 15px;
            margin-top: 20px;
            border-radius: 8px;
            font-size: 14px;
            color: #ccc;
        }

        .recommendation-note strong {
            color: #16B31E;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Midjourney 이미지 갤러리</h1>
        <div class="subtitle">원본 + 4개 크롭 이미지</div>
        <div class="stats">
            총 <strong>{count}</strong>개 원본 이미지 · <strong>{total_crops}</strong>개 크롭
        </div>

"""

    total_crops = 0

    for group in image_groups:
        original = group['original']
        crops = group['crops']
        total_crops += len(crops)

        # 추천 이미지 선택 (간단한 로직: crop_number 1 - top_left를 기본 추천)
        # 실제로는 AI를 사용해서 프롬프트와 가장 잘 맞는 이미지를 선택할 수 있음
        recommended_crop = crops[0] if crops else None

        html += f"""
        <div class="image-group">
            <div class="original-section">
                <div class="section-title">
                    <span class="badge">원본</span>
                    <span>Original Image</span>
                </div>
                <div class="image-id">ID: {original['image_id']}</div>
                <div class="prompt">{original['prompt']}</div>
                <img src="{original['public_url']}" alt="Original" class="original-image" loading="lazy">
                <div class="metadata">
                    <span>{original.get('width', 'N/A')}×{original.get('height', 'N/A')}</span>
                    <span>{original.get('format', 'png').upper()}</span>
                    <span>{original['created_at'][:10]}</span>
                </div>
            </div>

            <div class="section-title">
                <span class="badge">크롭</span>
                <span>Cropped Images ({len(crops)}개)</span>
            </div>
"""

        if crops:
            html += '<div class="crops-grid">'

            for idx, crop in enumerate(crops):
                is_recommended = (crop['image_id'] == recommended_crop['image_id']) if recommended_crop else False
                position_names = {
                    'top_left': '좌상단 (1번)',
                    'top_right': '우상단 (2번)',
                    'bottom_left': '좌하단 (3번)',
                    'bottom_right': '우하단 (4번)'
                }
                position_display = position_names.get(crop['crop_position'], crop['crop_position'])

                html += f"""
                <div class="crop-card {'recommended' if is_recommended else ''}">
                    <img src="{crop['public_url']}" alt="{crop['crop_position']}" class="crop-image" loading="lazy">
                    <div class="crop-info">
                        <div class="crop-position {'recommended' if is_recommended else ''}">
                            {position_display}
                            {'(추천)' if is_recommended else ''}
                        </div>
                        <div class="metadata">
                            <span>{crop.get('width', 'N/A')}×{crop.get('height', 'N/A')}</span>
                        </div>
                        <button class="copy-btn {'secondary' if not is_recommended else ''}"
                                onclick="copyUrl('{crop['public_url']}', '{crop['image_id']}')">
                            {'블로그에 사용' if is_recommended else 'URL 복사'}
                        </button>
                    </div>
                </div>
"""

            html += '</div>'

            if recommended_crop:
                html += f"""
                <div class="recommendation-note">
                    ⭐ <strong>추천 이미지:</strong> {position_names.get(recommended_crop['crop_position'], recommended_crop['crop_position'])} -
                    프롬프트 내용을 가장 잘 표현하는 크롭입니다. 블로그 글에 이 이미지를 사용하세요!
                </div>
"""
        else:
            html += '<p style="color: #666;">크롭 이미지가 없습니다.</p>'

        html += '</div>'  # image-group 종료

    html += """
    </div>

    <script>
        function copyUrl(url, imageId) {
            navigator.clipboard.writeText(url).then(() => {
                alert('URL이 복사되었습니다!\\n\\nImage ID: ' + imageId + '\\n\\n블로그 글에 붙여넣으세요.');
            });
        }
    </script>
</body>
</html>
"""

    html = html.replace("{count}", str(len(image_groups)))
    html = html.replace("{total_crops}", str(total_crops))

    output_path.write_text(html, encoding='utf-8')
    logger.success(f"✅ HTML 생성 완료: {output_path}")

def main():
    logger.info("=" * 60)
    logger.info("🖼️  Midjourney 이미지 조회 (크롭 포함)")
    logger.info("=" * 60)

    # 이미지 조회
    image_groups = fetch_images_with_crops()

    if not image_groups:
        logger.warning("⚠️  저장된 이미지가 없습니다")
        return

    logger.success(f"✅ {len(image_groups)}개 원본 이미지 발견")

    # HTML 생성
    output_path = Path(__file__).parent.parent / 'public' / 'midjourney_gallery_crops.html'
    output_path.parent.mkdir(exist_ok=True)

    generate_html_with_crops(image_groups, output_path)

    logger.info("\n" + "=" * 60)
    logger.info("🌐 갤러리 보기:")
    logger.info(f"   file://{output_path}")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()

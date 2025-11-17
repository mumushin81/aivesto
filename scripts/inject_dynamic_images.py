#!/usr/bin/env python3
"""
블로그 HTML에 Supabase에서 동적으로 이미지를 로드하는 스크립트 주입
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

def inject_dynamic_image_loader(html_file: Path, article_id: str):
    """HTML 파일에 동적 이미지 로딩 스크립트 주입"""

    if not html_file.exists():
        logger.error(f"❌ HTML 파일 없음: {html_file}")
        return False

    logger.info(f"📝 HTML 파일 처리 중: {html_file.name}")

    # HTML 읽기
    content = html_file.read_text(encoding='utf-8')

    # 이미 스크립트가 주입되어 있는지 확인
    if 'loadDynamicImages' in content:
        logger.info("  ℹ️  이미 동적 이미지 로더가 주입되어 있음")
        return True

    # Supabase 설정
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    # 동적 이미지 로딩 스크립트
    script = f"""
    <script>
        // Supabase에서 동적으로 이미지 로드
        async function loadDynamicImages() {{
            const SUPABASE_URL = '{supabase_url}';
            const SUPABASE_KEY = '{supabase_key}';
            const ARTICLE_ID = '{article_id}';

            try {{
                // blog_images 테이블에서 이미지 가져오기
                const response = await fetch(
                    `${{SUPABASE_URL}}/rest/v1/blog_images?article_id=eq.${{ARTICLE_ID}}&select=*,images(*)&order=position`,
                    {{
                        headers: {{
                            'apikey': SUPABASE_KEY,
                            'Authorization': `Bearer ${{SUPABASE_KEY}}`
                        }}
                    }}
                );

                if (!response.ok) {{
                    console.error('Failed to fetch images:', response.statusText);
                    return;
                }}

                const data = await response.json();
                console.log(`✅ Loaded ${{data.length}} images from Supabase`);

                // 기존 정적 이미지를 Supabase 이미지로 교체
                const contentDiv = document.querySelector('.content');
                if (!contentDiv) return;

                const imgTags = contentDiv.querySelectorAll('img');

                // 각 이미지 태그를 순서대로 교체
                data.forEach((record, index) => {{
                    if (index < imgTags.length && record.images) {{
                        const img = imgTags[index];
                        const newSrc = record.images.image_url;

                        // 이미지 URL 교체
                        img.src = newSrc;
                        img.alt = record.images.prompt || img.alt;

                        console.log(`  [${{index}}] Replaced with: ${{newSrc.substring(0, 60)}}...`);
                    }}
                }});

            }} catch (error) {{
                console.error('Error loading dynamic images:', error);
            }}
        }}

        // 페이지 로드 시 실행
        document.addEventListener('DOMContentLoaded', loadDynamicImages);
    </script>
"""

    # </body> 태그 바로 앞에 스크립트 삽입
    if '</body>' in content:
        content = content.replace('</body>', f'{script}\n</body>')
        logger.success("  ✅ 동적 이미지 로더 스크립트 주입 완료")
    else:
        logger.error("  ❌ </body> 태그를 찾을 수 없음")
        return False

    # 파일 저장
    html_file.write_text(content, encoding='utf-8')
    logger.success(f"  ✅ 파일 저장 완료: {html_file}")

    return True


def main():
    """메인 함수"""
    logger.info("=" * 60)
    logger.info("🔧 블로그 HTML에 동적 이미지 로더 주입")
    logger.info("=" * 60)

    # NVDA Blackwell 기사 HTML
    html_file = Path("/Users/jinxin/dev/aivesto/public/articles/article_NVDA_blackwell_gpu_20251113.html")
    article_id = "nvda_blackwell_20251113"

    success = inject_dynamic_image_loader(html_file, article_id)

    if success:
        logger.success("\n" + "=" * 60)
        logger.success("🎉 동적 이미지 로더 주입 완료!")
        logger.success("=" * 60)
        logger.info(f"\n브라우저에서 확인: file://{html_file.absolute()}")
        logger.info("\n브라우저 개발자 도구 콘솔에서 이미지 로딩 로그를 확인할 수 있습니다.")
    else:
        logger.error("\n❌ 스크립트 주입 실패")


if __name__ == "__main__":
    main()

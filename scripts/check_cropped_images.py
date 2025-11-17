#!/usr/bin/env python3
"""
미드저니 크롭된 이미지 확인 및 blog_images 업데이트
"""
import os
from dotenv import load_dotenv
from loguru import logger
from supabase import create_client

load_dotenv()

def check_and_fix_cropped_images():
    """크롭된 이미지 확인 및 images 테이블 업데이트"""

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        logger.error("❌ SUPABASE_URL/KEY 설정 누락")
        return False

    supabase = create_client(supabase_url, supabase_key)

    logger.info("=" * 60)
    logger.info("🔍 크롭된 이미지 확인 및 수정")
    logger.info("=" * 60)

    # 1단계: 현재 blog_images에 연결된 original 이미지 확인
    logger.info("\n📝 1단계: 현재 blog_images 연결 상태 확인 중...")

    try:
        blog_result = supabase.table('blog_images') \
            .select('*, images(*)') \
            .eq('article_id', 'nvda_blackwell_20251113') \
            .order('position') \
            .execute()

        if not blog_result.data:
            logger.error("❌ blog_images 테이블이 비어있음")
            return False

        logger.info(f"  ✅ {len(blog_result.data)}개 이미지 연결됨")

        current_images = []
        for record in blog_result.data:
            img = record.get('images', {})
            img_url = img.get('image_url', '')
            logger.info(f"  Position {record.get('position')}: {img_url[:80]}...")

            # /originals/ 경로에서 파일명 추출
            if '/originals/' in img_url:
                filename = img_url.split('/originals/')[-1]
                current_images.append({
                    'position': record.get('position'),
                    'image_id': record.get('image_id'),
                    'original_url': img_url,
                    'original_filename': filename
                })
                logger.warning(f"       ⚠️  ORIGINAL 이미지 (크롭 전)")

    except Exception as e:
        logger.error(f"❌ blog_images 조회 실패: {e}")
        return False

    # 2단계: midjourney_images에서 크롭된 버전 찾기
    logger.info("\n📝 2단계: 크롭된 이미지 검색 중...")

    cropped_mapping = {}

    for img_info in current_images:
        try:
            # 원본 파일명으로 midjourney_images에서 original 레코드 찾기
            original_result = supabase.table('midjourney_images') \
                .select('*') \
                .eq('image_type', 'original') \
                .ilike('public_url', f'%{img_info["original_filename"]}') \
                .execute()

            if not original_result.data:
                logger.warning(f"  ⚠️  Position {img_info['position']}: midjourney_images에서 original 레코드 못 찾음")
                continue

            original_record = original_result.data[0]
            original_id = original_record.get('id')

            logger.info(f"  Position {img_info['position']}: Original ID = {original_id}")

            # 이 original_id의 image_id를 parent_image_id로 갖는 cropped 이미지 찾기
            original_image_id = original_record.get('image_id')  # 예: "f5abc6f2b048"

            cropped_result = supabase.table('midjourney_images') \
                .select('*') \
                .eq('image_type', 'cropped') \
                .eq('parent_image_id', original_image_id) \
                .execute()

            if cropped_result.data:
                logger.success(f"       ✅ {len(cropped_result.data)}개 크롭 이미지 발견!")

                # 첫 번째 크롭 이미지 사용 (top_left)
                cropped_img = cropped_result.data[0]
                cropped_url = cropped_img.get('public_url', '')

                cropped_mapping[img_info['position']] = {
                    'image_id': img_info['image_id'],
                    'old_url': img_info['original_url'],
                    'new_url': cropped_url,
                    'cropped_record': cropped_img
                }

                logger.info(f"       NEW: {cropped_url[:80]}...")
            else:
                logger.warning(f"       ⚠️  크롭 이미지 없음 (parent_id={original_id})")

        except Exception as e:
            logger.error(f"  ❌ Position {img_info['position']} 처리 실패: {e}")
            continue

    # 3단계: images 테이블 업데이트
    logger.info("\n📝 3단계: images 테이블 업데이트 중...")

    if not cropped_mapping:
        logger.error("❌ 업데이트할 크롭 이미지가 없음")
        return False

    updated_count = 0

    for position, mapping in cropped_mapping.items():
        try:
            update_result = supabase.table('images') \
                .update({'image_url': mapping['new_url']}) \
                .eq('id', mapping['image_id']) \
                .execute()

            if update_result.data:
                logger.success(f"  ✅ Position {position}: images 테이블 업데이트 완료")
                logger.info(f"     OLD: {mapping['old_url'][:70]}...")
                logger.info(f"     NEW: {mapping['new_url'][:70]}...")
                updated_count += 1
            else:
                logger.error(f"  ❌ Position {position}: 업데이트 실패")

        except Exception as e:
            logger.error(f"  ❌ Position {position} 업데이트 실패: {e}")
            continue

    # 4단계: 검증
    logger.info("\n📝 4단계: 업데이트 결과 검증 중...")

    try:
        verify_result = supabase.table('blog_images') \
            .select('*, images(*)') \
            .eq('article_id', 'nvda_blackwell_20251113') \
            .order('position') \
            .execute()

        if verify_result.data:
            logger.success(f"\n✅ 검증 완료! {len(verify_result.data)}개 이미지 확인")
            logger.info("\n업데이트된 이미지:")

            for record in verify_result.data:
                img = record.get('images', {})
                img_url = img.get('image_url', '')

                if '/cropped/' in img_url:
                    logger.success(f"  Position {record.get('position')}: ✅ CROPPED - {img_url[:70]}...")
                elif '/originals/' in img_url:
                    logger.warning(f"  Position {record.get('position')}: ⚠️  ORIGINAL - {img_url[:70]}...")
                else:
                    logger.info(f"  Position {record.get('position')}: {img_url[:70]}...")

            return True
        else:
            logger.error("❌ blog_images 테이블이 비어있음")
            return False

    except Exception as e:
        logger.error(f"❌ 검증 실패: {e}")
        return False


if __name__ == "__main__":
    success = check_and_fix_cropped_images()

    if success:
        logger.success("\n" + "=" * 60)
        logger.success("🎉 크롭된 이미지로 업데이트 완료!")
        logger.success("==" * 60)
        logger.info("\n다음 단계:")
        logger.info("1. 로컬에서 HTML 확인: file:///Users/jinxin/dev/aivesto/public/articles/article_NVDA_blackwell_gpu_20251113.html")
        logger.info("2. GitHub 커밋 및 푸시")
        logger.info("3. Vercel 자동 배포 확인")
    else:
        logger.error("\n" + "=" * 60)
        logger.error("❌ 크롭 이미지 업데이트 실패")
        logger.error("=" * 60)

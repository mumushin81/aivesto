#!/usr/bin/env python3
"""
AI를 사용하여 4개 크롭 이미지 중 프롬프트에 가장 적합한 이미지를 자동으로 선택
Claude Vision API를 사용한 이미지 분석
"""
import os
import json
import base64
import requests
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client
from loguru import logger
from anthropic import Anthropic

# aivesto .env 로드
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(env_path)

supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")
if not anthropic_api_key:
    raise ValueError("ANTHROPIC_API_KEY must be set in .env file")

def download_image(url: str) -> bytes:
    """URL에서 이미지 다운로드"""
    response = requests.get(url)
    response.raise_for_status()
    return response.content

def analyze_crops_with_claude(prompt: str, crop_images: list) -> dict:
    """
    Claude Vision API로 4개 크롭 이미지 분석

    Args:
        prompt: 원본 Midjourney 프롬프트
        crop_images: [{'position': 'top_left', 'url': '...', 'image_id': '...'}, ...]

    Returns:
        {'best_crop': 'top_left', 'scores': {...}, 'reasoning': '...'}
    """
    client = Anthropic(api_key=anthropic_api_key)

    # 이미지 다운로드 및 base64 인코딩
    image_contents = []
    for crop in crop_images:
        try:
            img_data = download_image(crop['url'])
            b64_data = base64.b64encode(img_data).decode('utf-8')
            image_contents.append({
                'position': crop['position'],
                'b64': b64_data
            })
            logger.info(f"  {crop['position']} 이미지 다운로드 완료")
        except Exception as e:
            logger.error(f"  {crop['position']} 다운로드 실패: {e}")
            return None

    # Claude에게 분석 요청
    logger.info("🤖 Claude Vision으로 이미지 분석 중...")

    # 메시지 구성
    content = [
        {
            "type": "text",
            "text": f"""당신은 전문 이미지 큐레이터입니다. 다음 Midjourney 프롬프트로 생성된 원본 이미지를 4등분한 크롭 이미지들을 분석해주세요.

**원본 프롬프트:**
{prompt}

**분석 기준:**
1. 프롬프트 키워드와의 일치도
2. 구도 및 중심성 (주요 피사체가 중앙에 배치되었는가)
3. 시각적 임팩트 (조명, 색상, 대비)
4. 블로그 썸네일로서의 적합성
5. 전문성 및 완성도

다음 4개 이미지를 분석하고, 각 이미지에 대해 100점 만점으로 점수를 매긴 후, 가장 높은 점수의 이미지를 추천해주세요.

**출력 형식 (JSON):**
{{
  "scores": {{
    "top_left": 85,
    "top_right": 70,
    "bottom_left": 80,
    "bottom_right": 75
  }},
  "best_crop": "top_left",
  "reasoning": "top_left 이미지는 주요 피사체가 정중앙에 배치되어 있고, 드라마틱한 조명으로 강렬한 시각적 임팩트를 제공합니다..."
}}

이미지 순서: 1=top_left, 2=top_right, 3=bottom_left, 4=bottom_right"""
        }
    ]

    # 이미지 추가
    for idx, img in enumerate(image_contents, 1):
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": img['b64']
            }
        })
        content.append({
            "type": "text",
            "text": f"**Image {idx}: {img['position']}**"
        })

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": content
            }]
        )

        # 응답 파싱
        response_text = response.content[0].text
        logger.info(f"📊 Claude 분석 완료")
        logger.debug(f"응답: {response_text}")

        # JSON 추출 (```json ... ``` 블록에서)
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        else:
            # JSON만 있는 경우
            json_str = response_text.strip()

        result = json.loads(json_str)
        return result

    except Exception as e:
        logger.error(f"Claude API 오류: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_recommendation_in_db(parent_image_id: str, best_crop_position: str, scores: dict, reasoning: str):
    """추천 결과를 Supabase에 저장"""
    supabase = create_client(supabase_url, supabase_key)

    # 원본 이미지의 metadata에 추천 정보 저장
    metadata = {
        "ai_recommendation": {
            "best_crop": best_crop_position,
            "scores": scores,
            "reasoning": reasoning,
            "analyzed_at": "2025-11-16T15:35:00Z"
        }
    }

    supabase.table('midjourney_images')\
        .update({"metadata": metadata})\
        .eq('image_id', parent_image_id)\
        .execute()

    logger.success(f"✅ 추천 정보 DB 저장 완료: {best_crop_position}")

def main():
    logger.info("=" * 60)
    logger.info("🤖 AI 자동 크롭 이미지 선택")
    logger.info("=" * 60)

    supabase = create_client(supabase_url, supabase_key)

    # 원본 이미지 조회
    originals = supabase.table('midjourney_images')\
        .select('*')\
        .eq('image_type', 'original')\
        .order('created_at', desc=True)\
        .execute()

    if not originals.data:
        logger.warning("⚠️  원본 이미지가 없습니다")
        return

    logger.info(f"📥 {len(originals.data)}개 원본 이미지 발견\n")

    for idx, original in enumerate(originals.data, 1):
        logger.info(f"[{idx}/{len(originals.data)}] {original['image_id']}")
        logger.info(f"  프롬프트: {original['prompt'][:60]}...")

        # 크롭 이미지 조회
        crops = supabase.table('midjourney_images')\
            .select('*')\
            .eq('parent_image_id', original['image_id'])\
            .eq('image_type', 'cropped')\
            .order('crop_number')\
            .execute()

        if not crops.data or len(crops.data) != 4:
            logger.warning(f"  ⚠️  크롭 이미지가 {len(crops.data) if crops.data else 0}개입니다 (4개 필요)")
            continue

        logger.info(f"  ✓ 크롭 이미지 4개 확인")

        # 크롭 이미지 정보 구성
        crop_images = [{
            'position': crop['crop_position'],
            'url': crop['public_url'],
            'image_id': crop['image_id']
        } for crop in crops.data]

        # Claude로 분석
        result = analyze_crops_with_claude(original['prompt'], crop_images)

        if result:
            logger.success(f"  🏆 최고 추천: {result['best_crop']}")
            logger.info(f"  📊 점수:")
            for pos, score in result['scores'].items():
                emoji = "⭐" if pos == result['best_crop'] else "  "
                logger.info(f"     {emoji} {pos}: {score}점")
            logger.info(f"  💭 이유: {result['reasoning'][:100]}...")

            # DB에 저장
            update_recommendation_in_db(
                original['image_id'],
                result['best_crop'],
                result['scores'],
                result['reasoning']
            )
        else:
            logger.error(f"  ❌ 분석 실패")

        logger.info("")

    logger.info("=" * 60)
    logger.success("✅ 모든 이미지 분석 완료!")
    logger.info("=" * 60)

if __name__ == "__main__":
    main()

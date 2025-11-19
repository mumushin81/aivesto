"""이미지 처리 유틸리티 - 십자로 4등분 크롭"""
import os
from pathlib import Path
from typing import List
from PIL import Image
import logging

logger = logging.getLogger(__name__)


def crop_image_cross(image_path: str, output_dir: str = None) -> List[str]:
    """
    이미지를 십자로 수직 중앙, 수평 중앙 기준으로 4등분하여 크롭합니다.
    
    Args:
        image_path: 원본 이미지 경로
        output_dir: 출력 디렉토리 (None이면 원본과 같은 디렉토리)
    
    Returns:
        생성된 4개 이미지 파일 경로 리스트 [상단왼쪽, 상단오른쪽, 하단왼쪽, 하단오른쪽]
    """
    try:
        # 이미지 열기
        with Image.open(image_path) as img:
            width, height = img.size
            
            # 중앙 좌표 계산
            center_x = width // 2
            center_y = height // 2
            
            # 4개 영역 정의
            # 상단 왼쪽: (0, 0) ~ (center_x, center_y)
            # 상단 오른쪽: (center_x, 0) ~ (width, center_y)
            # 하단 왼쪽: (0, center_y) ~ (center_x, height)
            # 하단 오른쪽: (center_x, center_y) ~ (width, height)
            
            crops = [
                (0, 0, center_x, center_y),  # 상단 왼쪽
                (center_x, 0, width, center_y),  # 상단 오른쪽
                (0, center_y, center_x, height),  # 하단 왼쪽
                (center_x, center_y, width, height)  # 하단 오른쪽
            ]
            
            # 출력 디렉토리 설정
            if output_dir is None:
                output_dir = os.path.dirname(image_path)
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            # 원본 파일명에서 확장자 분리
            base_name = Path(image_path).stem
            ext = Path(image_path).suffix
            
            # 4개 이미지 크롭 및 저장
            output_paths = []
            crop_names = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
            
            for idx, (left, top, right, bottom) in enumerate(crops):
                crop_img = img.crop((left, top, right, bottom))
                
                output_filename = f"{base_name}_{crop_names[idx]}{ext}"
                output_path = os.path.join(output_dir, output_filename)
                
                crop_img.save(output_path, quality=95)
                output_paths.append(output_path)
                
                logger.info(
                    f"크롭 완료: {crop_names[idx]} "
                    f"({right-left}x{bottom-top}) -> {output_path}"
                )
            
            return output_paths
            
    except Exception as e:
        logger.error(f"이미지 크롭 실패: {e}")
        raise


def process_batch_images(image_paths: List[str], output_dir: str = None) -> List[List[str]]:
    """
    여러 이미지를 배치로 처리합니다.
    
    Args:
        image_paths: 원본 이미지 경로 리스트
        output_dir: 출력 디렉토리
    
    Returns:
        각 이미지별로 4개 크롭된 이미지 경로 리스트
    """
    results = []
    for image_path in image_paths:
        try:
            cropped_paths = crop_image_cross(image_path, output_dir)
            results.append(cropped_paths)
        except Exception as e:
            logger.error(f"이미지 처리 실패 {image_path}: {e}")
            results.append([])
    return results


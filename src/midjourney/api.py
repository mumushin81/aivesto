"""
Midjourney 편리한 API 함수들
다른 파일에서 쉽게 import해서 사용할 수 있는 고수준 함수들
"""
import logging
from typing import List, Optional, Dict, Any, Union
from pathlib import Path

from .client import (
    PassPromptToSelfBot,
    save_image_to_supabase,
    generate_images_batch,
    ImageGenerationResult
)
from .storage import MidjourneyImageStorage

logger = logging.getLogger(__name__)

# 전역 스토리지 인스턴스 (lazy initialization)
_storage_instance: Optional[MidjourneyImageStorage] = None


def _get_storage() -> MidjourneyImageStorage:
    """스토리지 인스턴스 가져오기 (싱글톤 패턴)"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = MidjourneyImageStorage()
    return _storage_instance


def generate_and_save_image(
    prompt: str,
    image_paths: Optional[List[Union[str, Path]]] = None,
    wait_for_completion: bool = True,
    timeout: int = 300,
    auto_crop: bool = True,
    verbose: bool = True
) -> Optional[Dict[str, Any]]:
    """
    이미지를 생성하고 Supabase에 저장합니다.
    
    Args:
        prompt: 이미지 생성 프롬프트
        image_paths: 참조 이미지 파일 경로 리스트 (선택사항)
        wait_for_completion: 이미지 완성까지 대기할지 여부
        timeout: 최대 대기 시간 (초)
        auto_crop: 자동 크롭 여부
        verbose: 상세 로그 출력 여부
    
    Returns:
        저장 결과 딕셔너리 또는 None (실패 시)
    
    Example:
        >>> result = generate_and_save_image("a beautiful sunset")
        >>> print(result['image_id'])
        >>> print(result['cropped_image_ids'])
    """
    try:
        from .client import wait_for_image_completion
        import time
        
        # 이미지 생성 요청
        if image_paths:
            image_paths_list = [Path(p) for p in image_paths]
        else:
            image_paths_list = None
        
        request_timestamp = time.time()
        response = PassPromptToSelfBot(prompt, image_paths=image_paths_list)
        
        if response.status_code != 204:
            if verbose:
                logger.error(f"이미지 생성 요청 실패: HTTP {response.status_code}")
            return None
        
        if not wait_for_completion:
            return {
                "success": True,
                "status": "requested",
                "message": "이미지 생성 요청 완료. 완성까지 대기하지 않음."
            }
        
        # 이미지 완성 대기
        if verbose:
            logger.info("이미지 완성 대기 중...")
        
        image_urls = wait_for_image_completion(
            prompt=prompt,
            request_timestamp=request_timestamp,
            timeout=timeout,
            check_interval=5
        )
        
        if not image_urls:
            if verbose:
                logger.warning("이미지 생성 타임아웃")
            return None
        
        # 첫 번째 이미지만 저장 (일반적으로 1개)
        if image_urls:
            result = save_image_from_url(
                image_url=image_urls[0],
                prompt=prompt,
                auto_crop=auto_crop,
                verbose=verbose
            )
            return result
        
        return None
        
    except Exception as e:
        logger.error(f"이미지 생성 및 저장 실패: {e}")
        return None


def save_image_from_url(
    image_url: str,
    prompt: str,
    auto_crop: bool = True,
    metadata: Optional[Dict[str, Any]] = None,
    verbose: bool = True
) -> Optional[Dict[str, Any]]:
    """
    이미지 URL에서 이미지를 다운로드하여 Supabase에 저장합니다.
    
    Args:
        image_url: 다운로드할 이미지 URL
        prompt: 생성 프롬프트
        auto_crop: 자동 크롭 여부 (기본값: True)
        metadata: 추가 메타데이터
        verbose: 상세 로그 출력 여부
    
    Returns:
        저장 결과 딕셔너리 또는 None (실패 시)
    
    Example:
        >>> result = save_image_from_url(
        ...     image_url="https://cdn.discordapp.com/...",
        ...     prompt="a beautiful sunset"
        ... )
        >>> print(result['image_id'])
        >>> print(result['cropped_image_ids'])
    """
    try:
        storage = _get_storage()
        result = storage.save_midjourney_image_from_url(
            image_url=image_url,
            prompt=prompt,
            auto_crop=auto_crop,
            metadata=metadata
        )
        
        if result.get('success'):
            if verbose:
                logger.info(f"이미지 저장 완료: {result.get('image_id')}")
            return result
        else:
            if verbose:
                logger.error(f"이미지 저장 실패: {result.get('error')}")
            return None
            
    except Exception as e:
        logger.error(f"이미지 저장 중 오류: {e}")
        return None


def delete_image(
    image_id: str,
    delete_all: bool = False,
    verbose: bool = True
) -> bool:
    """
    이미지를 Supabase에서 삭제합니다.
    
    Args:
        image_id: 삭제할 이미지 ID
        delete_all: True이면 원본과 모든 크롭 이미지 삭제, False이면 해당 이미지만 삭제
        verbose: 상세 로그 출력 여부
    
    Returns:
        삭제 성공 여부
    
    Example:
        >>> # 개별 이미지 삭제
        >>> delete_image("crop_image_id", delete_all=False)
        >>> # 전체 삭제 (원본 + 모든 크롭)
        >>> delete_image("original_image_id", delete_all=True)
    """
    try:
        storage = _get_storage()
        success = storage.delete_image(image_id, delete_all=delete_all)
        
        if verbose:
            if success:
                logger.info(f"이미지 삭제 완료: {image_id}")
            else:
                logger.warning(f"이미지 삭제 실패: {image_id}")
        
        return success
        
    except Exception as e:
        logger.error(f"이미지 삭제 중 오류: {e}")
        return False


def get_image(image_id: str) -> Optional[Dict[str, Any]]:
    """
    이미지 ID로 이미지 정보를 가져옵니다.
    
    Args:
        image_id: 이미지 ID
    
    Returns:
        이미지 정보 딕셔너리 또는 None
    
    Example:
        >>> image = get_image("image_id_123")
        >>> print(image['public_url'])
    """
    try:
        storage = _get_storage()
        return storage.get_image_by_id(image_id)
    except Exception as e:
        logger.error(f"이미지 조회 중 오류: {e}")
        return None


def get_image_group(original_image_id: str) -> Optional[Dict[str, Any]]:
    """
    원본 이미지와 모든 크롭 이미지를 함께 가져옵니다.
    
    Args:
        original_image_id: 원본 이미지 ID
    
    Returns:
        원본 이미지와 크롭 이미지 정보 딕셔너리 또는 None
    
    Example:
        >>> group = get_image_group("original_id")
        >>> print(group['original']['public_url'])
        >>> for crop in group['cropped']:
        ...     print(crop['public_url'])
    """
    try:
        storage = _get_storage()
        return storage.get_image_group(original_image_id)
    except Exception as e:
        logger.error(f"이미지 그룹 조회 중 오류: {e}")
        return None


def list_images(
    limit: int = 100,
    original_only: bool = True,
    prompt: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    이미지 목록을 가져옵니다.
    
    Args:
        limit: 가져올 개수
        original_only: True이면 원본 이미지만 가져오기
        prompt: 특정 프롬프트로 필터링 (선택사항)
    
    Returns:
        이미지 정보 리스트
    
    Example:
        >>> # 모든 원본 이미지 가져오기
        >>> images = list_images(limit=50)
        >>> # 특정 프롬프트의 이미지 가져오기
        >>> images = list_images(prompt="a beautiful sunset")
    """
    try:
        storage = _get_storage()
        
        if prompt:
            return storage.get_images_by_prompt(prompt, limit=limit)
        else:
            return storage.get_all_images(limit=limit, original_only=original_only)
            
    except Exception as e:
        logger.error(f"이미지 목록 조회 중 오류: {e}")
        return []


def generate_images_batch_and_save(
    prompts: List[str],
    image_paths_per_prompt: Optional[
        List[Optional[List[Union[str, Path]]]]
    ] = None,
    request_delay: float = 2.0,
    timeout_per_image: int = 300,
    auto_crop: bool = True,
    save_locally: bool = False,
    verbose: bool = True
) -> List[ImageGenerationResult]:
    """
    여러 프롬프트를 배치로 생성하고 Supabase에 저장합니다.
    
    Args:
        prompts: 이미지 생성 프롬프트 리스트
        image_paths_per_prompt: 각 프롬프트에 대한 참조 이미지 경로 리스트
        request_delay: 각 요청 사이의 대기 시간 (초)
        timeout_per_image: 각 이미지당 최대 대기 시간 (초)
        auto_crop: 자동 크롭 여부
        save_locally: 로컬 파일 시스템에도 저장할지 여부
        verbose: 상세 로그 출력 여부
    
    Returns:
        ImageGenerationResult 리스트
    
    Example:
        >>> results = generate_images_batch_and_save(
        ...     prompts=["sunset", "cityscape"],
        ...     auto_crop=True
        ... )
        >>> for result in results:
        ...     print(result.supabase_image_ids)
    """
    return generate_images_batch(
        prompts=prompts,
        image_paths_per_prompt=image_paths_per_prompt,
        request_delay=request_delay,
        timeout_per_image=timeout_per_image,
        auto_crop=auto_crop,
        auto_upload=True,  # 항상 Supabase에 저장
        save_locally=save_locally,
        verbose=verbose
    )


def delete_images_by_prompt(
    prompt: str,
    delete_all: bool = True,
    verbose: bool = True
) -> int:
    """
    특정 프롬프트의 모든 이미지를 삭제합니다.
    
    Args:
        prompt: 삭제할 프롬프트
        delete_all: True이면 원본과 모든 크롭 이미지 삭제
        verbose: 상세 로그 출력 여부
    
    Returns:
        삭제된 이미지 그룹 개수
    
    Example:
        >>> count = delete_images_by_prompt("a beautiful sunset")
        >>> print(f"{count}개 이미지 그룹 삭제 완료")
    """
    try:
        storage = _get_storage()
        count = storage.delete_images_by_prompt(prompt, delete_all=delete_all)
        
        if verbose:
            logger.info(f"프롬프트 '{prompt}'의 이미지 {count}개 그룹 삭제 완료")
        
        return count
        
    except Exception as e:
        logger.error(f"프롬프트별 이미지 삭제 중 오류: {e}")
        return 0


def upload_reference_image(image_path: Union[str, Path]) -> Optional[str]:
    """
    참조 이미지를 Discord에 업로드하고 URL을 반환합니다.
    
    Args:
        image_path: 업로드할 이미지 파일 경로
    
    Returns:
        업로드된 이미지 URL 또는 None
    
    Example:
        >>> url = upload_reference_image("reference.png")
        >>> result = generate_and_save_image(
        ...     prompt="similar style",
        ...     image_paths=[url]
        ... )
    """
    try:
        from .client import upload_image_to_discord
        image_path_obj = Path(image_path)
        
        if not image_path_obj.exists():
            logger.error(f"이미지 파일을 찾을 수 없습니다: {image_path}")
            return None
        
        return upload_image_to_discord(image_path_obj)
        
    except Exception as e:
        logger.error(f"이미지 업로드 중 오류: {e}")
        return None


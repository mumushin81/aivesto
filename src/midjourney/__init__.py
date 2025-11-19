"""Midjourney 이미지 생성 및 관리 모듈"""
from .client import (
    PassPromptToSelfBot,
    Upscale,
    MaxUpscale,
    Variation,
    get_channel_messages,
    extract_image_urls_from_message,
    find_initial_job_message,
    match_prompt_to_message,
    wait_for_image_completion,
    download_image,
    generate_images_batch,
    save_image_to_supabase,
    ImageGenerationResult
)

from .processor import (
    crop_image_cross,
    process_batch_images
)

from .manager import PromptManager

from .storage import MidjourneyImageStorage

from .prompt_generator import (
    MidjourneyPromptGenerator,
    generate_midjourney_prompt
)

# 편리한 API 함수들
from .api import (
    generate_and_save_image,
    save_image_from_url,
    delete_image,
    get_image,
    get_image_group,
    list_images,
    generate_images_batch_and_save,
    delete_images_by_prompt,
    upload_reference_image
)

__all__ = [
    # Client functions
    'PassPromptToSelfBot',
    'Upscale',
    'MaxUpscale',
    'Variation',
    'get_channel_messages',
    'extract_image_urls_from_message',
    'find_initial_job_message',
    'match_prompt_to_message',
    'wait_for_image_completion',
    'download_image',
    'generate_images_batch',
    'save_image_to_supabase',
    'ImageGenerationResult',
    # Processor functions
    'crop_image_cross',
    'process_batch_images',
    # Manager classes
    'PromptManager',
    # Storage classes
    'MidjourneyImageStorage',
    # Prompt generator
    'MidjourneyPromptGenerator',
    'generate_midjourney_prompt',
    # 편리한 API 함수들
    'generate_and_save_image',
    'save_image_from_url',
    'delete_image',
    'get_image',
    'get_image_group',
    'list_images',
    'generate_images_batch_and_save',
    'delete_images_by_prompt',
    'upload_reference_image',
]


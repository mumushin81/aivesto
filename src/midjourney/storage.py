"""Midjourney 이미지 Supabase 저장 관리"""
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from src.supabase.image_storage import ImageStorageManager

logger = logging.getLogger(__name__)


class MidjourneyImageStorage(ImageStorageManager):
    """Midjourney 이미지 전용 저장 관리자"""
    
    def __init__(self):
        """Midjourney 이미지용 버킷으로 초기화"""
        super().__init__()
        self.image_bucket = "midjourney-images"
        self._ensure_image_bucket_exists()
    
    def _ensure_image_bucket_exists(self):
        """Midjourney 이미지 버킷이 존재하는지 확인하고 없으면 생성"""
        try:
            buckets_response = self.client.storage.list_buckets()
            # buckets_response는 StorageListBucketsResponse 객체
            buckets = buckets_response.data if hasattr(buckets_response, 'data') else []
            bucket_exists = any(
                bucket.name == self.image_bucket if hasattr(bucket, 'name') 
                else bucket.get('name') == self.image_bucket 
                for bucket in buckets
            )
            
            if not bucket_exists:
                # 버킷 생성 시도
                try:
                    self.client.storage.create_bucket(
                        self.image_bucket,
                        options={'public': True}
                    )
                    logger.info(f"Midjourney 이미지 버킷 생성 완료: {self.image_bucket}")
                except Exception as create_error:
                    logger.warning(
                        f"버킷 자동 생성 실패 (수동 생성 필요): {create_error}\n"
                        f"Supabase 대시보드에서 '{self.image_bucket}' 버킷을 수동으로 생성해주세요."
                    )
            else:
                logger.info(f"Midjourney 이미지 버킷 확인 완료: {self.image_bucket}")
        except Exception as e:
            logger.warning(f"버킷 확인 실패: {e}")
    
    def save_midjourney_image(
        self,
        image_path: str,
        prompt: str,
        original_url: Optional[str] = None,
        cropped_paths: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        auto_crop: bool = True
    ) -> Dict[str, Any]:
        """
        Midjourney 이미지와 메타데이터를 Supabase에 저장합니다.
        
        Args:
            image_path: 원본 이미지 경로
            prompt: 생성 프롬프트
            original_url: 원본 Discord URL
            cropped_paths: 크롭된 이미지 경로 리스트
            metadata: 추가 메타데이터
        
        Returns:
            저장 결과
        """
        try:
            from PIL import Image
            
            # 이미지 정보 가져오기
            with Image.open(image_path) as img:
                width, height = img.size
                format_name = img.format.lower() if img.format else 'png'
            
            file_size = os.path.getsize(image_path)
            filename = Path(image_path).name
            
            # 고유 ID 생성 (타임스탬프 + 파일명 해시)
            import hashlib
            unique_id = hashlib.md5(
                f"{datetime.now().isoformat()}_{filename}".encode()
            ).hexdigest()[:12]
            
            # 원본 이미지 업로드
            storage_path = f"originals/{unique_id}_{filename}"
            content_type = f"image/{format_name}"
            
            with open(image_path, 'rb') as f:
                self.client.storage.from_(self.image_bucket).upload(
                    path=storage_path,
                    file=f,
                    file_options={"content-type": content_type}
                )
            
            public_url = self.client.storage.from_(self.image_bucket).get_public_url(storage_path)
            
            # 원본 이미지 DB 레코드 생성
            db_record = {
                "image_id": unique_id,
                "prompt": prompt,
                "original_url": original_url or public_url,
                "storage_path": storage_path,
                "public_url": public_url,
                "width": width,
                "height": height,
                "file_size": file_size,
                "format": format_name,
                "image_type": "original",
                "generation_model": "midjourney",
                "generated_at": datetime.now().isoformat(),
                "metadata": metadata or {},
                "cropped_images": []  # 하위 호환성을 위해 유지
            }
            
            # 원본 이미지 DB에 저장
            try:
                response = self.client.table('midjourney_images').insert(db_record).execute()
                logger.info(f"원본 이미지 메타데이터 저장 완료: {unique_id}")
            except Exception as e:
                logger.error(f"원본 이미지 DB 저장 실패: {e}")
                raise
            
            # 크롭된 이미지 처리
            cropped_image_ids = []
            cropped_urls = []
            
            # 크롭이 필요하고 아직 크롭되지 않은 경우 자동 크롭
            if auto_crop and not cropped_paths:
                try:
                    from .processor import crop_image_cross
                    import tempfile
                    temp_dir = tempfile.mkdtemp()
                    cropped_paths = crop_image_cross(image_path, temp_dir)
                    logger.info(f"자동 크롭 완료: {len(cropped_paths)}개 이미지")
                except Exception as e:
                    logger.warning(f"자동 크롭 실패: {e}")
                    cropped_paths = []
            
            # 크롭된 이미지들을 개별 레코드로 저장
            if cropped_paths:
                crop_positions = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
                
                for idx, cropped_path in enumerate(cropped_paths):
                    if idx >= len(crop_positions):
                        break
                    
                    try:
                        # 크롭된 이미지 정보 가져오기
                        with Image.open(cropped_path) as crop_img:
                            crop_width, crop_height = crop_img.size
                        crop_file_size = os.path.getsize(cropped_path)
                        crop_name = Path(cropped_path).name
                        
                        # 크롭된 이미지 고유 ID 생성
                        crop_unique_id = hashlib.md5(
                            f"{unique_id}_crop_{idx+1}_{crop_name}".encode()
                        ).hexdigest()[:12]
                        
                        # Storage에 업로드 (폴더 구조: cropped/{원본ID}/1.png, 2.png, 3.png, 4.png)
                        crop_storage_path = f"cropped/{unique_id}/{idx+1}.png"
                        
                        with open(cropped_path, 'rb') as f:
                            self.client.storage.from_(self.image_bucket).upload(
                                path=crop_storage_path,
                                file=f,
                                file_options={"content-type": content_type}
                            )
                        
                        crop_url = self.client.storage.from_(self.image_bucket).get_public_url(crop_storage_path)
                        
                        # 크롭된 이미지를 개별 DB 레코드로 저장
                        crop_db_record = {
                            "image_id": crop_unique_id,
                            "parent_image_id": unique_id,
                            "prompt": prompt,
                            "original_url": crop_url,
                            "storage_path": crop_storage_path,
                            "public_url": crop_url,
                            "width": crop_width,
                            "height": crop_height,
                            "file_size": crop_file_size,
                            "format": format_name,
                            "image_type": "cropped",
                            "crop_position": crop_positions[idx],
                            "crop_number": idx + 1,
                            "generation_model": "midjourney",
                            "generated_at": datetime.now().isoformat(),
                            "metadata": {
                                **(metadata or {}),
                                "parent_image_id": unique_id,
                                "crop_index": idx
                            }
                        }
                        
                        self.client.table('midjourney_images').insert(crop_db_record).execute()
                        
                        cropped_image_ids.append(crop_unique_id)
                        cropped_urls.append({
                            "image_id": crop_unique_id,
                            "position": crop_positions[idx],
                            "crop_number": idx + 1,
                            "url": crop_url,
                            "storage_path": crop_storage_path
                        })
                        
                        logger.info(f"크롭 이미지 저장 완료: {crop_unique_id} ({crop_positions[idx]})")
                        
                    except Exception as e:
                        logger.error(f"크롭 이미지 {idx+1} 저장 실패: {e}")
                        continue
                    
                    finally:
                        # 임시 파일 정리
                        if auto_crop and os.path.exists(cropped_path):
                            try:
                                os.unlink(cropped_path)
                            except Exception:
                                pass
                
                # 임시 디렉토리 정리
                if auto_crop and 'temp_dir' in locals():
                    try:
                        import shutil
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    except Exception:
                        pass
            
            return {
                "success": True,
                "image_id": unique_id,
                "original_url": public_url,
                "cropped_image_ids": cropped_image_ids,
                "cropped_urls": cropped_urls,
                "storage_path": storage_path
            }
            
        except Exception as e:
            logger.error(f"이미지 저장 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_all_images(self, limit: int = 100, original_only: bool = True) -> List[Dict[str, Any]]:
        """
        모든 Midjourney 이미지 가져오기
        
        Args:
            limit: 가져올 개수
            original_only: True이면 원본 이미지만 가져오기 (기본값: True)
        """
        try:
            query = self.client.table('midjourney_images').select("*")
            if original_only:
                query = query.eq('image_type', 'original')
            response = query.order("generated_at", desc=True).limit(limit).execute()
            return response.data or []
        except Exception as e:
            logger.warning(f"이미지 목록 가져오기 실패: {e}")
            return []
    
    def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """ID로 이미지 가져오기"""
        try:
            response = self.client.table('midjourney_images').select("*").eq('image_id', image_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"이미지 가져오기 실패: {e}")
            return None
    
    def get_images_by_prompt(self, prompt: str, limit: int = 100) -> List[Dict[str, Any]]:
        """프롬프트로 이미지 검색"""
        try:
            response = self.client.table('midjourney_images').select("*").eq('prompt', prompt).order("generated_at", desc=True).limit(limit).execute()
            return response.data or []
        except Exception as e:
            logger.warning(f"프롬프트 검색 실패: {e}")
            return []
    
    def save_midjourney_image_from_url(
        self,
        image_url: str,
        prompt: str,
        cropped_paths: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        auto_crop: bool = True
    ) -> Dict[str, Any]:
        """
        이미지 URL에서 직접 다운로드하여 Supabase에 저장합니다.
        자동으로 크롭하여 4장의 이미지를 개별 레코드로 저장합니다.
        
        Args:
            image_url: 다운로드할 이미지 URL
            prompt: 생성 프롬프트
            cropped_paths: 크롭된 이미지 경로 리스트 (None이면 자동 크롭)
            metadata: 추가 메타데이터
            auto_crop: 자동 크롭 여부 (기본값: True)
        
        Returns:
            저장 결과 (original_image_id, cropped_image_ids 포함)
        """
        import requests
        import tempfile
        
        try:
            # 임시 파일로 다운로드
            from . import config as Globals
            header = {
                'authorization': Globals.SALAI_TOKEN
            }
            response = requests.get(image_url, headers=header, stream=True, timeout=30)
            
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"이미지 다운로드 실패: HTTP {response.status_code}"
                }
            
            # 임시 파일에 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    tmp_file.write(chunk)
                tmp_path = tmp_file.name
            
            try:
                # Supabase에 저장 (자동 크롭 포함)
                result = self.save_midjourney_image(
                    image_path=tmp_path,
                    prompt=prompt,
                    original_url=image_url,
                    cropped_paths=cropped_paths,
                    metadata=metadata,
                    auto_crop=auto_crop
                )
                return result
            finally:
                # 임시 파일 삭제
                try:
                    os.unlink(tmp_path)
                except Exception:
                    pass
                    
        except Exception as e:
            logger.error(f"URL에서 이미지 저장 실패: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_image(self, image_id: str, delete_all: bool = False) -> bool:
        """
        이미지를 Supabase Storage와 DB에서 삭제합니다.
        
        Args:
            image_id: 삭제할 이미지 ID
            delete_all: True이면 원본과 모든 크롭 이미지 삭제, False이면 해당 이미지만 삭제
        
        Returns:
            삭제 성공 여부
        """
        try:
            # DB에서 이미지 정보 가져오기
            image_info = self.get_image_by_id(image_id)
            if not image_info:
                logger.warning(f"이미지를 찾을 수 없습니다: {image_id}")
                return False
            
            image_type = image_info.get('image_type', 'original')
            
            if delete_all and image_type == 'original':
                # 원본 이미지와 모든 크롭 이미지 삭제
                return self._delete_image_group(image_id)
            else:
                # 개별 이미지만 삭제
                return self._delete_single_image(image_id, image_info)
            
        except Exception as e:
            logger.error(f"이미지 삭제 실패: {e}")
            return False
    
    def _delete_single_image(self, image_id: str, image_info: Dict[str, Any]) -> bool:
        """개별 이미지 삭제"""
        try:
            storage_path = image_info.get('storage_path')
            if storage_path:
                try:
                    self.client.storage.from_(self.image_bucket).remove([storage_path])
                    logger.info(f"Storage에서 삭제 완료: {storage_path}")
                except Exception as e:
                    logger.warning(f"Storage 삭제 실패: {e}")
            
            # DB에서 레코드 삭제
            self.client.table('midjourney_images').delete().eq('image_id', image_id).execute()
            logger.info(f"DB에서 삭제 완료: {image_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"개별 이미지 삭제 실패: {e}")
            return False
    
    def _delete_image_group(self, original_image_id: str) -> bool:
        """원본 이미지와 모든 크롭 이미지 삭제"""
        try:
            # 원본 이미지 정보 가져오기
            original_info = self.get_image_by_id(original_image_id)
            if not original_info:
                logger.warning(f"원본 이미지를 찾을 수 없습니다: {original_image_id}")
                return False
            
            # 모든 크롭된 이미지 가져오기
            cropped_images = self.client.table('midjourney_images').select(
                "image_id, storage_path"
            ).eq('parent_image_id', original_image_id).eq('image_type', 'cropped').execute()
            
            # Storage에서 삭제할 경로 수집
            paths_to_delete = []
            
            # 원본 이미지 경로 추가
            if original_info.get('storage_path'):
                paths_to_delete.append(original_info['storage_path'])
            
            # 크롭된 이미지 경로 추가
            cropped_ids = []
            for crop in cropped_images.data or []:
                if crop.get('storage_path'):
                    paths_to_delete.append(crop['storage_path'])
                if crop.get('image_id'):
                    cropped_ids.append(crop['image_id'])
            
            # Storage에서 일괄 삭제
            if paths_to_delete:
                try:
                    self.client.storage.from_(self.image_bucket).remove(paths_to_delete)
                    logger.info(f"Storage에서 {len(paths_to_delete)}개 파일 삭제 완료")
                except Exception as e:
                    logger.warning(f"Storage 일괄 삭제 실패: {e}")
            
            # DB에서 원본과 모든 크롭 이미지 삭제
            # CASCADE로 인해 parent_image_id가 있으면 자동 삭제되지만, 명시적으로 삭제
            if cropped_ids:
                self.client.table('midjourney_images').delete().in_('image_id', cropped_ids).execute()
                logger.info(f"크롭된 이미지 {len(cropped_ids)}개 DB 삭제 완료")
            
            self.client.table('midjourney_images').delete().eq('image_id', original_image_id).execute()
            logger.info(f"원본 이미지 DB 삭제 완료: {original_image_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"이미지 그룹 삭제 실패: {e}")
            return False
    
    def delete_images_by_prompt(self, prompt: str, delete_all: bool = True) -> int:
        """
        특정 프롬프트의 모든 이미지를 삭제합니다.
        
        Args:
            prompt: 삭제할 프롬프트
            delete_all: True이면 원본과 모든 크롭 이미지 삭제
        
        Returns:
            삭제된 원본 이미지 그룹 개수
        """
        try:
            # 원본 이미지만 가져오기 (image_type='original')
            images = self.client.table('midjourney_images').select(
                "image_id"
            ).eq('prompt', prompt).eq('image_type', 'original').execute()
            
            deleted_count = 0
            
            for image in images.data or []:
                image_id = image.get('image_id')
                if image_id and self.delete_image(image_id, delete_all=delete_all):
                    deleted_count += 1
            
            logger.info(f"프롬프트 '{prompt}'의 이미지 그룹 {deleted_count}개 삭제 완료")
            return deleted_count
            
        except Exception as e:
            logger.error(f"프롬프트별 이미지 삭제 실패: {e}")
            return 0
    
    def get_image_group(self, original_image_id: str) -> Optional[Dict[str, Any]]:
        """
        원본 이미지와 모든 크롭 이미지를 함께 가져옵니다.
        
        Args:
            original_image_id: 원본 이미지 ID
        
        Returns:
            원본 이미지와 크롭 이미지 정보
        """
        try:
            # 원본 이미지 가져오기
            original = self.get_image_by_id(original_image_id)
            if not original or original.get('image_type') != 'original':
                return None
            
            # 크롭된 이미지들 가져오기
            cropped = self.client.table('midjourney_images').select(
                "*"
            ).eq('parent_image_id', original_image_id).eq('image_type', 'cropped').order(
                'crop_number'
            ).execute()
            
            return {
                "original": original,
                "cropped": cropped.data or []
            }
            
        except Exception as e:
            logger.error(f"이미지 그룹 가져오기 실패: {e}")
            return None


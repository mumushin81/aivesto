"""Extended Supabase client with image storage capabilities."""
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import mimetypes
from PIL import Image

from .client import SupabaseManager

logger = logging.getLogger(__name__)


class ImageStorageManager(SupabaseManager):
    """Extended Supabase manager with image storage capabilities."""
    
    def __init__(self):
        """Initialize with image-specific bucket."""
        super().__init__()
        self.image_bucket = "book-images"
        self._ensure_image_bucket_exists()
    
    def _ensure_image_bucket_exists(self):
        """Ensure the image bucket exists."""
        try:
            buckets = self.client.storage.list_buckets()
            bucket_exists = any(bucket['name'] == self.image_bucket for bucket in buckets)
            
            if not bucket_exists:
                self.client.storage.create_bucket(
                    self.image_bucket,
                    options={'public': True}
                )
                logger.info(f"Created image bucket: {self.image_bucket}")
            else:
                logger.info(f"Image bucket already exists: {self.image_bucket}")
        except Exception as e:
            logger.warning(f"Could not check/create image bucket: {e}")
    
    def upload_book_image(
        self, 
        image_path: str, 
        document_id: str,
        image_type: str = "cover",
        variation: int = 1
    ) -> Dict[str, Any]:
        """
        Upload book image to Supabase storage.
        
        Args:
            image_path: Local path to image file
            document_id: Associated document ID
            image_type: Type of image (cover, illustration, etc.)
            variation: Variation number for multiple versions
            
        Returns:
            Upload result with storage info
        """
        try:
            # Validate image file
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            # Verify it's a valid image
            with Image.open(image_path) as img:
                width, height = img.size
                format_name = img.format.lower() if img.format else 'unknown'
            
            # Generate storage path
            file_name = Path(image_path).name
            storage_path = f"{image_type}s/{document_id}/{variation}_{file_name}"
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(image_path)
            if not content_type:
                content_type = "image/png"
            
            # Upload to storage
            with open(image_path, 'rb') as f:
                response = self.client.storage.from_(self.image_bucket).upload(
                    path=storage_path,
                    file=f,
                    file_options={"content-type": content_type}
                )
            
            # Get public URL
            public_url = self.client.storage.from_(self.image_bucket).get_public_url(storage_path)
            
            result = {
                "success": True,
                "storage_path": storage_path,
                "public_url": public_url,
                "content_type": content_type,
                "width": width,
                "height": height,
                "format": format_name,
                "file_size": os.path.getsize(image_path)
            }
            
            logger.info(f"Uploaded image: {storage_path}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to upload image {image_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path
            }
    
    def store_image_metadata(
        self,
        document_id: str,
        image_data: Dict[str, Any],
        prompt_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Store image metadata in database.
        
        Args:
            document_id: Associated document ID
            image_data: Image file and storage information
            prompt_data: AI prompt and generation data
            
        Returns:
            Database insert result
        """
        try:
            metadata = {
                "document_id": document_id,
                "storage_path": image_data.get("storage_path"),
                "public_url": image_data.get("public_url"),
                "width": image_data.get("width"),
                "height": image_data.get("height"),
                "file_size": image_data.get("file_size"),
                "content_type": image_data.get("content_type"),
                "image_type": "book_cover",
                "generation_model": image_data.get("model", "qwen/qwen-image"),
                "generation_time": image_data.get("generation_time"),
                "prompt_text": image_data.get("prompt"),
                "metadata": {
                    "prompt_data": prompt_data,
                    "replicate_url": str(image_data.get("image_url", "")),
                    "local_path": str(image_data.get("local_path", "")),
                    "thumbnail_path": str(image_data.get("thumbnail_path", ""))
                }
            }
            
            # Insert into book_images table
            response = self.client.table('book_images').insert(metadata).execute()
            
            logger.info(f"Stored image metadata for document: {document_id}")
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to store image metadata: {e}")
            raise
    
    def get_document_images(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all images for a document."""
        try:
            response = self.client.table('book_images').select("*").eq('document_id', document_id).execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to get document images: {e}")
            return []
    
    def get_image_by_id(self, image_id: str) -> Optional[Dict[str, Any]]:
        """Get specific image by ID."""
        try:
            response = self.client.table('book_images').select("*").eq('id', image_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get image: {e}")
            return None
    
    def delete_image(self, image_id: str) -> bool:
        """Delete image from storage and database."""
        try:
            # Get image info first
            image_info = self.get_image_by_id(image_id)
            if not image_info:
                return False
            
            # Delete from storage
            if image_info.get('storage_path'):
                try:
                    self.client.storage.from_(self.image_bucket).remove([image_info['storage_path']])
                except Exception as e:
                    logger.warning(f"Failed to delete from storage: {e}")
            
            # Delete from database
            self.client.table('book_images').delete().eq('id', image_id).execute()
            
            logger.info(f"Deleted image: {image_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete image: {e}")
            return False
    
    def update_document_with_images(
        self,
        document_id: str,
        image_ids: List[str],
        primary_image_id: str = None
    ):
        """Update document record with associated images."""
        try:
            update_data = {
                "image_ids": image_ids,
                "primary_image_id": primary_image_id or (image_ids[0] if image_ids else None),
                "has_images": len(image_ids) > 0
            }
            
            response = self.client.table('text_documents').update(update_data).eq('id', document_id).execute()
            
            logger.info(f"Updated document {document_id} with {len(image_ids)} images")
            return response.data[0] if response.data else {}
            
        except Exception as e:
            logger.error(f"Failed to update document with images: {e}")
            raise
"""Upload Midjourney images to Supabase storage + DB metadata tables."""
import os
import mimetypes
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from dotenv import load_dotenv
from loguru import logger
from supabase import create_client, Client


load_dotenv()


class SupabaseImageUploader:
    def __init__(
        self,
        bucket: str = "blog-images",
        images_table: str = "images",
        blog_images_table: str = "blog_images",
    ):
        self.supabase_url = os.getenv("SUPABASE_URL")
        # Prefer service role for storage write; fallback to regular key.
        self.supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_KEY")
        if not self.supabase_url or not self.supabase_key:
            raise RuntimeError("SUPABASE_URL/SUPABASE_KEY missing; check .env")

        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.bucket = bucket
        self.images_table = images_table
        self.blog_images_table = blog_images_table

        self._ensure_bucket()

    # ------------------------- Storage helpers -------------------------
    def _ensure_bucket(self):
        try:
            # Idempotent: will raise if exists; ignore.
            self.client.storage.create_bucket(self.bucket, public=True)
            logger.info(f"Created storage bucket '{self.bucket}'")
        except Exception:
            logger.debug(f"Bucket '{self.bucket}' already exists")

    def upload_image(self, file_path: Path, object_name: Optional[str] = None) -> str:
        object_name = object_name or file_path.name
        mime_type, _ = mimetypes.guess_type(file_path)
        with open(file_path, "rb") as f:
            res = self.client.storage.from_(self.bucket).upload(
                path=object_name,
                file=f,
                file_options={"content-type": mime_type or "image/jpeg"},
            )
            if res.get("error"):
                raise RuntimeError(f"Upload failed: {res['error']}")

        public_url = (
            self.client.storage.from_(self.bucket)
            .get_public_url(object_name, {
                "download": False,
                "transform": {"width": 1200},  # ensure usable hero size
            })
        )
        logger.info(f"Uploaded image to {public_url}")
        return public_url

    # ------------------------- DB helpers -------------------------
    def insert_image_row(
        self,
        *,
        symbol: str,
        topic: str,
        prompt: str,
        image_url: str,
        section_title: str | None = None,
        context_keywords: list | None = None,
        image_type: str | None = None,
        caption: str | None = None,
    ) -> str:
        payload = {
            "symbol": symbol,
            "topic": topic,
            "prompt": prompt,
            "image_url": image_url,
            "section_title": section_title,
            "context_keywords": context_keywords,
            "image_type": image_type,
            "caption": caption,
            "created_at": datetime.utcnow().isoformat(),
        }
        result = self.client.table(self.images_table).insert(payload).execute()
        image_id = result.data[0]["id"]
        logger.info(f"Inserted image row {image_id}")
        return image_id

    def link_to_article(self, *, article_id: str, image_id: str, position: int = 0) -> None:
        payload = {
            "article_id": article_id,
            "image_id": image_id,
            "position": position,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.client.table(self.blog_images_table).upsert(payload, on_conflict="article_id,image_id").execute()
        logger.info(f"Linked image {image_id} to article {article_id} at position {position}")

    # ------------------------- Combined convenience -------------------------
    def upload_and_record(
        self,
        *,
        file_path: Path,
        symbol: str,
        topic: str,
        prompt: str,
        article_id: Optional[str] = None,
        position: int = 0,
        section_title: Optional[str] = None,
        context_keywords: Optional[list] = None,
        image_type: Optional[str] = None,
        caption: Optional[str] = None,
    ) -> Tuple[str, str]:
        public_url = self.upload_image(file_path)
        image_id = self.insert_image_row(
            symbol=symbol,
            topic=topic,
            prompt=prompt,
            image_url=public_url,
            section_title=section_title,
            context_keywords=context_keywords,
            image_type=image_type,
            caption=caption,
        )
        if article_id:
            self.link_to_article(article_id=article_id, image_id=image_id, position=position)
        return image_id, public_url


__all__ = ["SupabaseImageUploader"]

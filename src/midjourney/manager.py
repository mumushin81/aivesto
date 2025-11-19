"""프롬프트와 이미지 매핑 관리"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib
import logging

logger = logging.getLogger(__name__)


class PromptManager:
    """프롬프트와 이미지 파일 매핑을 관리하는 클래스"""
    
    def __init__(self, metadata_file: str = None):
        """
        Args:
            metadata_file: 메타데이터 JSON 파일 경로
        """
        if metadata_file is None:
            base_dir = Path(__file__).parent.parent.parent
            metadata_file = str(base_dir / "data" / "images" / "prompt_metadata.json")
        
        self.metadata_file = Path(metadata_file)
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
        self.metadata = self._load_metadata()
    
    def _load_metadata(self) -> Dict:
        """메타데이터 파일 로드"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"메타데이터 로드 실패: {e}")
                return {}
        return {}
    
    def _save_metadata(self):
        """메타데이터 파일 저장"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"메타데이터 저장 실패: {e}")
    
    def get_prompt_hash(self, prompt: str) -> str:
        """프롬프트의 해시값 생성"""
        return hashlib.md5(prompt.encode()).hexdigest()[:12]
    
    def register_image(
        self,
        prompt: str,
        original_path: str,
        cropped_paths: List[str],
        image_urls: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        이미지와 프롬프트를 등록합니다.
        
        Returns:
            prompt_hash: 프롬프트 해시값
        """
        prompt_hash = self.get_prompt_hash(prompt)
        
        if prompt_hash not in self.metadata:
            self.metadata[prompt_hash] = {
                "prompt": prompt,
                "created_at": datetime.now().isoformat(),
                "images": []
            }
        
        image_entry = {
            "original_path": str(original_path),
            "cropped_paths": [str(p) for p in cropped_paths],
            "image_urls": image_urls or [],
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.metadata[prompt_hash]["images"].append(image_entry)
        self._save_metadata()
        
        return prompt_hash
    
    def get_prompt_groups(self) -> List[Dict]:
        """프롬프트별 그룹 리스트 반환"""
        groups = []
        for prompt_hash, data in self.metadata.items():
            groups.append({
                "prompt_hash": prompt_hash,
                "prompt": data["prompt"],
                "created_at": data["created_at"],
                "image_count": len(data["images"]),
                "latest_image": data["images"][-1] if data["images"] else None
            })
        # 최신순 정렬
        groups.sort(key=lambda x: x["created_at"], reverse=True)
        return groups
    
    def get_images_by_prompt(self, prompt_hash: str) -> List[Dict]:
        """특정 프롬프트의 모든 이미지 반환"""
        if prompt_hash not in self.metadata:
            return []
        return self.metadata[prompt_hash]["images"]
    
    def delete_prompt_group(self, prompt_hash: str) -> bool:
        """프롬프트 그룹 전체 삭제"""
        if prompt_hash in self.metadata:
            del self.metadata[prompt_hash]
            self._save_metadata()
            return True
        return False
    
    def delete_image(self, prompt_hash: str, image_index: int) -> bool:
        """특정 이미지 삭제"""
        if prompt_hash in self.metadata:
            images = self.metadata[prompt_hash]["images"]
            if 0 <= image_index < len(images):
                images.pop(image_index)
                # 이미지가 없으면 그룹도 삭제
                if not images:
                    del self.metadata[prompt_hash]
                self._save_metadata()
                return True
        return False
    
    def get_prompt_by_hash(self, prompt_hash: str) -> Optional[str]:
        """해시로 프롬프트 가져오기"""
        if prompt_hash in self.metadata:
            return self.metadata[prompt_hash]["prompt"]
        return None
    
    def get_all_prompts(self) -> Dict[str, str]:
        """모든 프롬프트 해시-텍스트 매핑 반환"""
        return {
            hash_val: data["prompt"]
            for hash_val, data in self.metadata.items()
        }


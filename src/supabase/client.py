"""Supabase client configuration and initialization."""
import os
import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class SupabaseManager:
    """Manages Supabase storage and database operations."""
    
    def __init__(self):
        """Initialize Supabase client with appropriate keys for different operations."""
        self.url = os.environ.get("SUPABASE_URL")
        self.anon_key = os.environ.get("SUPABASE_ANON_KEY")
        self.service_key = os.environ.get("SUPABASE_SERVICE_KEY")

        if not self.url:
            raise ValueError("SUPABASE_URL must be set in environment variables")

        # Use anon key for read operations by default
        if not self.anon_key:
            raise ValueError("SUPABASE_ANON_KEY must be set in environment variables")

        self.client: Client = create_client(self.url, self.anon_key)

        # Create separate client with service key for storage/admin operations
        if self.service_key:
            self.admin_client: Client = create_client(self.url, self.service_key)
            logger.info("Supabase client initialized with service key for storage operations")
        else:
            self.admin_client = None
            logger.warning("SUPABASE_SERVICE_KEY not set - storage operations may fail")

        self.storage_bucket = "text-documents"
        logger.info("Supabase client initialized successfully")
    
    def upload_file_to_storage(self, file_path: str, storage_path: str) -> Dict[str, Any]:
        """
        Upload a file to Supabase storage using service key.

        Args:
            file_path: Local path to the file
            storage_path: Path in storage bucket

        Returns:
            Response from Supabase storage
        """
        if not self.admin_client:
            raise ValueError("SUPABASE_SERVICE_KEY required for storage operations")

        try:
            with open(file_path, 'rb') as file:
                response = self.admin_client.storage.from_(self.storage_bucket).upload(
                    path=storage_path,
                    file=file,
                    file_options={"content-type": "text/plain; charset=utf-8"}
                )
            logger.info(f"File uploaded successfully: {storage_path}")
            return response
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise
    
    def create_signed_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """
        Create a signed URL for a file in private storage.

        Args:
            storage_path: Path in storage bucket
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            Signed URL string
        """
        if not self.admin_client:
            raise ValueError("SUPABASE_SERVICE_KEY required for signed URL generation")

        try:
            response = self.admin_client.storage.from_(self.storage_bucket).create_signed_url(
                storage_path,
                expires_in
            )
            return response.get('signedURL', '')
        except Exception as e:
            logger.error(f"Failed to create signed URL: {e}")
            raise

    def get_public_url(self, storage_path: str) -> str:
        """
        Get public URL for a file in storage.

        Note: This only works if the bucket is public.
        For private buckets, use create_signed_url() instead.
        """
        response = self.client.storage.from_(self.storage_bucket).get_public_url(storage_path)
        return response
    
    def insert_text_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert text metadata to database.
        
        Args:
            metadata: Dictionary containing text metadata
            
        Returns:
            Response from database insert
        """
        try:
            response = self.client.table('text_documents').insert(metadata).execute()
            logger.info(f"Metadata inserted for: {metadata.get('title', 'Unknown')}")
            return response.data
        except Exception as e:
            logger.error(f"Failed to insert metadata: {e}")
            raise
    
    def update_summary(self, doc_id: str, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update document with summary information.
        
        Args:
            doc_id: Document ID
            summary_data: Summary data to update
            
        Returns:
            Response from database update
        """
        try:
            response = self.client.table('text_documents').update(summary_data).eq('id', doc_id).execute()
            logger.info(f"Summary updated for document: {doc_id}")
            return response.data
        except Exception as e:
            logger.error(f"Failed to update summary: {e}")
            raise
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Get all documents from database."""
        try:
            response = self.client.table('text_documents').select("*").execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to get documents: {e}")
            raise
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by ID."""
        try:
            response = self.client.table('text_documents').select("*").eq('id', doc_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Failed to get document: {e}")
            raise
    
    def create_bucket_if_not_exists(self):
        """Create storage bucket if it doesn't exist (requires service key)."""
        if not self.admin_client:
            logger.warning("SUPABASE_SERVICE_KEY not set - cannot create bucket")
            return

        try:
            # Try to get bucket info using admin client
            buckets = self.admin_client.storage.list_buckets()
            bucket_exists = any(bucket['name'] == self.storage_bucket for bucket in buckets)

            if not bucket_exists:
                # Create private bucket by default for security
                # Use create_signed_url() for access to private files
                self.admin_client.storage.create_bucket(
                    self.storage_bucket,
                    options={'public': False}
                )
                logger.info(f"Created private storage bucket: {self.storage_bucket}")
            else:
                logger.info(f"Storage bucket already exists: {self.storage_bucket}")
        except Exception as e:
            logger.warning(f"Could not check/create bucket: {e}")
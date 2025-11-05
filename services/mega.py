"""
MEGA cloud storage service implementation.
Handles file uploads to MEGA using mega.py library.
"""
import logging
from pathlib import Path
from typing import Optional
import asyncio
from functools import partial
import threading

logger = logging.getLogger(__name__)

# Try to import mega.py, but gracefully handle if not available
try:
    from mega import Mega
    MEGA_AVAILABLE = True
except ImportError:
    logger.warning("mega.py not available. MEGA service will not function.")
    Mega = None
    MEGA_AVAILABLE = False


class MegaService:
    """Service for uploading files to MEGA cloud storage."""
    
    def __init__(self, email: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize MEGA service.
        
        Args:
            email: MEGA account email
            password: MEGA account password
        """
        if not MEGA_AVAILABLE:
            logger.error("MEGA service initialized but mega.py is not available")
        
        self.email = email
        self.password = password
        self._mega_instance = None
        self._logged_in = False
        self._lock = threading.Lock()  # Thread-safe instance creation
    
    def _get_mega_instance(self) -> Mega:
        """Get or create MEGA instance (thread-safe)."""
        with self._lock:
            if self._mega_instance is None:
                self._mega_instance = Mega()
            return self._mega_instance
    
    def _login(self) -> bool:
        """
        Login to MEGA account.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        if self._logged_in:
            return True
            
        if not self.email or not self.password:
            logger.error("MEGA credentials not provided")
            return False
        
        try:
            mega = self._get_mega_instance()
            mega.login(self.email, self.password)
            self._logged_in = True
            logger.info("Successfully logged in to MEGA")
            return True
        except Exception as e:
            logger.error(f"Failed to login to MEGA: {str(e)}")
            return False
    
    async def upload_file(self, file_path: str) -> Optional[str]:
        """
        Upload a file to MEGA asynchronously.
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            Optional[str]: Public link to the uploaded file, or None if upload failed
        """
        if not MEGA_AVAILABLE:
            logger.error("Cannot upload to MEGA: mega.py library not available")
            return None
            
        try:
            # Run blocking MEGA operations in thread pool
            loop = asyncio.get_event_loop()
            
            # Login if not already logged in
            if not self._logged_in:
                login_result = await loop.run_in_executor(None, self._login)
                if not login_result:
                    return None
            
            # Upload file
            logger.info(f"Starting upload to MEGA: {file_path}")
            mega = self._get_mega_instance()
            
            # Upload file in thread pool to avoid blocking
            uploaded_file = await loop.run_in_executor(
                None,
                partial(mega.upload, file_path)
            )
            
            # Get public link
            link = await loop.run_in_executor(
                None,
                partial(mega.get_upload_link, uploaded_file)
            )
            
            logger.info(f"Successfully uploaded to MEGA: {link}")
            return link
            
        except Exception as e:
            logger.error(f"Failed to upload file to MEGA: {str(e)}")
            return None


# Global MEGA service instance
_mega_service: Optional[MegaService] = None


def get_mega_service(email: Optional[str] = None, password: Optional[str] = None) -> MegaService:
    """
    Get or create MEGA service instance.
    
    Args:
        email: MEGA account email
        password: MEGA account password
        
    Returns:
        MegaService: MEGA service instance
    """
    global _mega_service
    if _mega_service is None:
        _mega_service = MegaService(email, password)
    return _mega_service

"""
FastAPI Backend Server for Cloud Storage API
Handles file uploads, downloads, and link generation for multiple cloud storage providers.
"""
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional
import aiofiles
import asyncio

from fastapi import FastAPI, File, UploadFile, HTTPException, Header, Query, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from config import settings
from services.mega import get_mega_service

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan (startup and shutdown)."""
    # Startup
    logger.info("Starting Paimon Cloud Storage Server")
    
    # Create temporary upload directory if it doesn't exist
    temp_dir = Path(settings.temp_upload_dir)
    temp_dir.mkdir(exist_ok=True)
    logger.info(f"Temporary upload directory: {temp_dir.absolute()}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Paimon Cloud Storage Server")


# Initialize FastAPI app
app = FastAPI(
    title="Paimon Cloud Storage API",
    description="Backend server for cloud storage operations",
    version="1.0.0",
    lifespan=lifespan
)


# Authentication middleware
async def verify_auth_token(x_auth_token: Optional[str] = Header(None)):
    """
    Verify authentication token from request header.
    
    Args:
        x_auth_token: Authentication token from X-Auth-Token header
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not x_auth_token:
        logger.warning("Missing authentication token")
        raise HTTPException(status_code=401, detail="Missing authentication token")
    
    if x_auth_token != settings.auth_token:
        logger.warning(f"Invalid authentication token: {x_auth_token}")
        raise HTTPException(status_code=403, detail="Invalid authentication token")


@app.get("/ping")
async def ping():
    """
    Simple ping endpoint for connectivity testing.
    
    Returns:
        dict: Status message
    """
    logger.debug("Ping request received")
    return {"message": "Server running"}


@app.get("/status")
async def status():
    """
    Health check endpoint with basic server information.
    
    Returns:
        dict: Server status information
    """
    logger.debug("Status request received")
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Paimon Cloud Storage API",
        "temp_dir": settings.temp_upload_dir,
        "supported_services": ["mega"]
    }


@app.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    service: str = Query("mega", description="Cloud storage service to use"),
    x_auth_token: Optional[str] = Header(None)
):
    """
    Upload a file to the specified cloud storage service.
    
    Args:
        file: File to upload
        service: Cloud storage service name (default: mega)
        x_auth_token: Authentication token
        
    Returns:
        dict: Upload status and file link
        
    Raises:
        HTTPException: If authentication fails, service is unsupported, or upload fails
    """
    # Verify authentication
    await verify_auth_token(x_auth_token)
    
    # Validate service
    service = service.lower()
    if service not in ["mega"]:
        logger.error(f"Unsupported service requested: {service}")
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported service: {service}. Supported services: mega"
        )
    
    # Validate file
    if not file.filename:
        logger.error("No filename provided")
        raise HTTPException(status_code=400, detail="No filename provided")
    
    temp_file_path = None
    
    try:
        # Log upload start
        logger.info(f"Upload started - File: {file.filename}, Service: {service}, Size: {file.size if hasattr(file, 'size') else 'unknown'}")
        
        # Create temporary file
        temp_dir = Path(settings.temp_upload_dir)
        temp_dir.mkdir(exist_ok=True)
        
        # Generate safe temporary filename
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(
            mode='wb',
            delete=False,
            dir=temp_dir,
            suffix=suffix
        ) as temp_file:
            temp_file_path = temp_file.name
            
            # Read and write file content asynchronously
            content = await file.read()
            temp_file.write(content)
        
        logger.info(f"File saved temporarily at: {temp_file_path}")
        
        # Upload to selected service
        if service == "mega":
            mega_service = get_mega_service(settings.mega_email, settings.mega_password)
            file_link = await mega_service.upload_file(temp_file_path)
            
            if not file_link:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to upload file to MEGA. Check server logs for details."
                )
            
            logger.info(f"Upload completed - File: {file.filename}, Link: {file_link}")
            
            return {
                "status": "success",
                "message": "File uploaded successfully",
                "filename": file.filename,
                "service": service,
                "link": file_link
            }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except Exception as e:
        logger.error(f"Upload failed - File: {file.filename}, Error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )
        
    finally:
        # Cleanup: delete temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.debug(f"Temporary file deleted: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_file_path}: {str(e)}")


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    
    Args:
        request: Request object
        exc: Exception that was raised
        
    Returns:
        JSONResponse: Error response
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "detail": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "server:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        log_level=settings.log_level.lower()
    )

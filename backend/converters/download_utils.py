"""
Async Download Utilities
Memory-efficient streaming downloads for large 3D model files
"""
import aiohttp
import aiofiles
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Optimal chunk size for streaming (4MB)
CHUNK_SIZE = 4 * 1024 * 1024


async def download_file_streaming(
    url: str, 
    dest_path: str,
    chunk_size: int = CHUNK_SIZE,
    timeout: int = 300
) -> str:
    """
    Download large files using async streaming to avoid loading entire file into memory.
    
    Args:
        url: URL to download from
        dest_path: Destination file path
        chunk_size: Size of chunks to download (default: 4MB)
        timeout: Request timeout in seconds (default: 5 minutes)
        
    Returns:
        str: Path to downloaded file
        
    Raises:
        aiohttp.ClientError: If download fails
        IOError: If file write fails
    """
    logger.info(f"[Download] Starting streaming download: {url}")
    
    # Ensure destination directory exists
    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
    
    timeout_config = aiohttp.ClientTimeout(total=timeout)
    
    try:
        async with aiohttp.ClientSession(timeout=timeout_config) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise aiohttp.ClientError(
                        f"Download failed with status {response.status}: {url}"
                    )
                
                # Get file size if available
                file_size = response.headers.get('Content-Length')
                if file_size:
                    file_size_mb = int(file_size) / (1024 * 1024)
                    logger.info(f"[Download] File size: {file_size_mb:.2f}MB")
                
                # Stream download in chunks
                downloaded = 0
                async with aiofiles.open(dest_path, 'wb') as f:
                    async for chunk in response.content.iter_chunked(chunk_size):
                        await f.write(chunk)
                        downloaded += len(chunk)
                
                # Log completion
                downloaded_mb = downloaded / (1024 * 1024)
                logger.info(f"[Download] ✓ Completed: {downloaded_mb:.2f}MB → {dest_path}")
                
                return dest_path
                
    except aiohttp.ClientError as e:
        logger.error(f"[Download] ✗ Network error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"[Download] ✗ Unexpected error: {str(e)}")
        raise


async def download_multiple_files(
    urls: list[str],
    dest_dir: str,
    filename_prefix: str = "file"
) -> list[str]:
    """
    Download multiple files concurrently using asyncio.gather().
    
    Args:
        urls: List of URLs to download
        dest_dir: Destination directory
        filename_prefix: Prefix for generated filenames
        
    Returns:
        list[str]: Paths to downloaded files
    """
    import asyncio
    from pathlib import Path
    
    Path(dest_dir).mkdir(parents=True, exist_ok=True)
    
    tasks = []
    for i, url in enumerate(urls):
        ext = Path(url).suffix or '.bin'
        dest_path = f"{dest_dir}/{filename_prefix}_{i}{ext}"
        tasks.append(download_file_streaming(url, dest_path))
    
    # Download all files concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out errors
    successful_downloads = [
        r for r in results if not isinstance(r, Exception)
    ]
    
    logger.info(f"[Download] Downloaded {len(successful_downloads)}/{len(urls)} files")
    
    return successful_downloads

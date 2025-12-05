"""
File Cache Module
SHA256-based caching to avoid redundant processing of identical images
"""
import hashlib
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

CACHE_DIR = "data/cache"


def get_file_hash(filepath: str) -> str:
    """
    Generate SHA256 hash for cache key.
    Uses streaming to handle large files efficiently.
    
    Args:
        filepath: Path to file to hash
        
    Returns:
        str: SHA256 hash (hex)
    """
    sha256 = hashlib.sha256()
    
    with open(filepath, 'rb') as f:
        # Read in 8KB chunks
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    
    return sha256.hexdigest()


def get_cache_path(image_hash: str) -> str:
    """Get path to cache file for given image hash."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    return f"{CACHE_DIR}/3d_assets_{image_hash}.json"


async def get_cached_result(image_path: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached 3D generation result if available.
    
    Args:
        image_path: Path to input image
        
    Returns:
        dict | None: Cached result, or None if not in cache
    """
    try:
        image_hash = get_file_hash(image_path)
        cache_path = get_cache_path(image_hash)
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                result = json.load(f)
            
            logger.info(f"[Cache] ✓ Hit: {image_hash[:8]}...")
            return result
        
        logger.debug(f"[Cache] Miss: {image_hash[:8]}...")
        return None
        
    except Exception as e:
        logger.warning(f"[Cache] Error reading cache: {e}")
        return None


async def save_to_cache(image_path: str, result: Dict[str, Any]) -> None:
    """
    Save 3D generation result to cache.
    
    Args:
        image_path: Path to input image
        result: Result dictionary to cache
    """
    try:
        image_hash = get_file_hash(image_path)
        cache_path = get_cache_path(image_hash)
        
        # Ensure cache directory exists
        os.makedirs(CACHE_DIR, exist_ok=True)
        
        with open(cache_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"[Cache] ✓ Saved: {image_hash[:8]}...")
        
    except Exception as e:
        logger.warning(f"[Cache] Error saving cache: {e}")


def clear_cache() -> int:
    """
    Clear all cached results.
    
    Returns:
        int: Number of files deleted
    """
    if not os.path.exists(CACHE_DIR):
        return 0
    
    count = 0
    for filename in os.listdir(CACHE_DIR):
        if filename.startswith("3d_assets_") and filename.endswith(".json"):
            os.remove(os.path.join(CACHE_DIR, filename))
            count += 1
    
    logger.info(f"[Cache] Cleared {count} cached results")
    return count

"""
GLB to MP4 Converter
Generates 360° turntable video from GLB 3D models using trimesh + ffmpeg
"""
import trimesh
import numpy as np
from PIL import Image
import subprocess
import uuid
import os
import shutil
import logging
import io
from pathlib import Path

logger = logging.getLogger(__name__)


async def glb_to_mp4_simple(
    glb_path: str,
    output_mp4: str,
    num_frames: int = 60,
    fps: int = 10,
    resolution: tuple[int, int] = (800, 600)
) -> str:
    """
    Generate simple 360° turntable video from GLB model.
    Uses trimesh for rendering and ffmpeg for video encoding.
    
    Args:
        glb_path: Path to input GLB file
        output_mp4: Path to output MP4 file
        num_frames: Number of frames for full rotation (default: 60)
        fps: Frames per second (default: 10 = 6 second video)
        resolution: Output resolution as (width, height)
        
    Returns:
        str: Path to generated MP4 file
        
    Raises:
        FileNotFoundError: If GLB file doesn't exist
        RuntimeError: If rendering or encoding fails
    """
    logger.info(f"[GLB→MP4] Starting conversion: {glb_path}")
    
    if not os.path.exists(glb_path):
        raise FileNotFoundError(f"GLB file not found: {glb_path}")
    
    # Run in executor to avoid blocking async loop
    import asyncio
    loop = asyncio.get_event_loop()
    
    def _convert_sync():
        try:
            # Load GLB model
            logger.info(f"[GLB→MP4] Loading model...")
            mesh = trimesh.load(glb_path, force='mesh')
            
            # Create scene
            scene = mesh.scene()
            
            # Setup temp directory for frames
            temp_dir = f"/tmp/glb2mp4_{uuid.uuid4().hex[:8]}"
            os.makedirs(temp_dir, exist_ok=True)
            
            try:
                # Render frames with rotation
                logger.info(f"[GLB→MP4] Rendering {num_frames} frames...")
                for i in range(num_frames):
                    angle = (i / num_frames) * 360  # Full 360° rotation
                    
                    # Rotation matrix (around Y-axis)
                    transform = trimesh.transformations.rotation_matrix(
                        np.radians(angle),
                        [0, 1, 0],  # Y-axis (vertical)
                        [0, 0, 0]   # Origin
                    )
                    
                    # Render frame
                    try:
                        png_data = scene.save_image(
                            resolution=list(resolution),
                            transform=transform
                        )
                        
                        # Save frame
                        img = Image.open(io.BytesIO(png_data))
                        frame_path = f"{temp_dir}/frame_{i:04d}.png"
                        img.save(frame_path)
                        
                    except Exception as e:
                        logger.warning(f"[GLB→MP4] Frame {i} render failed: {e}")
                        # Use blank frame as fallback
                        blank = Image.new('RGB', resolution, color='white')
                        blank.save(f"{temp_dir}/frame_{i:04d}.png")
                
                # Check if we have frames
                frames = sorted([f for f in os.listdir(temp_dir) if f.endswith('.png')])
                if len(frames) < num_frames * 0.5:  # At least 50% frames must exist
                    raise RuntimeError(f"Too many frame rendering failures: {len(frames)}/{num_frames}")
                
                # Ensure output directory exists
                Path(output_mp4).parent.mkdir(parents=True, exist_ok=True)
                
                # Convert frames to MP4 using ffmpeg
                logger.info(f"[GLB→MP4] Encoding video with ffmpeg...")
                result = subprocess.run([
                    'ffmpeg',
                    '-y',  # Overwrite output file
                    '-framerate', str(fps),
                    '-i', f'{temp_dir}/frame_%04d.png',
                    '-c:v', 'libx264',
                    '-pix_fmt', 'yuv420p',
                    '-crf', '23',  # Quality (lower = better, 23 is good default)
                    '-preset', 'medium',  # Encoding speed vs compression
                    output_mp4
                ], capture_output=True, text=True, check=False)
                
                if result.returncode != 0:
                    logger.error(f"[GLB→MP4] FFmpeg error: {result.stderr}")
                    raise RuntimeError(f"FFmpeg encoding failed: {result.stderr[:200]}")
                
                # Verify output file exists and has content
                if not os.path.exists(output_mp4) or os.path.getsize(output_mp4) == 0:
                    raise RuntimeError("MP4 file was not created or is empty")
                
                file_size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
                logger.info(f"[GLB→MP4] ✓ Completed: {file_size_mb:.2f}MB → {output_mp4}")
                
                return output_mp4
                
            finally:
                # Cleanup temp frames
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    logger.debug(f"[GLB→MP4] Cleaned up temp directory")
        
        except Exception as e:
            logger.error(f"[GLB→MP4] ✗ Conversion failed: {str(e)}")
            raise RuntimeError(f"GLB to MP4 conversion failed: {str(e)}")
    
    # Execute in thread pool
    result = await loop.run_in_executor(None, _convert_sync)
    return result

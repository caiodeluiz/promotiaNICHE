"""
Listify Pipeline Steps
Orchestrates AI/ML services to transform product images into marketplace listings
"""
import os
import json
import asyncio
from typing import Dict, Any
from io import BytesIO
import base64

# AI/ML imports
from openai import OpenAI
import replicate
from rembg import remove
from PIL import Image
import requests

# Local imports
from backend.vision import detect_labels
from backend.classifier import classify_product

# Environment variables
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")


async def analyze_image(image_path: str) -> Dict[str, Any]:
    """
    Step 1: Analyze product image using Google Cloud Vision
    Extracts detailed attributes and classifies product niche
    
    Args:
        image_path: Path to the uploaded product image
        
    Returns:
        dict: {
            "attributes": {...},
            "niche": {...},
            "labels": [...],
            "confidence": float
        }
    """
    try:
        print(f"[Pipeline Step 1] Analyzing image: {image_path}")
        
        # Detect labels using Google Cloud Vision
        labels = detect_labels(image_path)
        
        # Classify product niche
        classification = classify_product(labels)
        
        # Extract detailed attributes
        attributes = {
            "detected_objects": labels[:10],  # Top 10 labels
            "primary_category": classification.get("niche_name", "Unknown"),
            "confidence_score": classification.get("confidence", 0.0)
        }
        
        result = {
            "attributes": attributes,
            "niche": {
                "id": classification.get("niche_id"),
                "name": classification.get("niche_name"),
                "description": classification.get("description", "")
            },
            "labels": labels,
            "confidence": classification.get("confidence", 0.0)
        }
        
        print(f"[Pipeline Step 1] ✓ Analysis complete: {classification.get('niche_name')}")
        return result
        
    except Exception as e:
        print(f"[Pipeline Step 1] ✗ Error: {str(e)}")
        raise


async def research_price(image_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 2: Research market price based on product attributes
    Uses heuristic pricing based on category
    
    Args:
        image_analysis: Output from analyze_image()
        
    Returns:
        dict: {
            "estimated_price": float,
            "price_range": {"min": float, "max": float},
            "currency": str,
            "confidence": str
        }
    """
    try:
        print(f"[Pipeline Step 2] Researching price...")
        
        niche_name = image_analysis["niche"]["name"]
        
        # Heuristic price ranges by category (in USD)
        price_ranges = {
            "Fitness & Wellness": (15, 150),
            "Pet Supplies": (10, 80),
            "Home Office": (30, 300),
            "Beauty & Personal Care": (10, 100),
            "Tech Accessories": (15, 120),
            "Outdoor & Adventure": (25, 200),
            "Kitchen & Dining": (20, 150),
            "Fashion & Apparel": (20, 200),
            "Gaming": (30, 400),
            "Home Decor": (25, 250),
            "Baby & Kids": (15, 120),
            "Automotive": (20, 180),
            "Gardening": (15, 100),
            "Books & Media": (10, 50),
            "Art & Crafts": (10, 80),
        }
        
        # Get price range for niche, or use default
        min_price, max_price = price_ranges.get(niche_name, (20, 100))
        estimated_price = (min_price + max_price) / 2
        
        result = {
            "estimated_price": round(estimated_price, 2),
            "price_range": {
                "min": min_price,
                "max": max_price
            },
            "currency": "USD",
            "confidence": "medium"
        }
        
        print(f"[Pipeline Step 2] ✓ Price estimated: ${estimated_price:.2f}")
        return result
        
    except Exception as e:
        print(f"[Pipeline Step 2] ✗ Error: {str(e)}")
        raise


async def generate_content(product_attributes: Dict[str, Any], price_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 3: Generate SEO-optimized product listing content using Qwen-Flash LLM
    
    Args:
        product_attributes: Output from analyze_image()
        price_data: Output from research_price()
        
    Returns:
        dict: {
            "title": str,
            "description": str,
            "bullet_points": list,
            "tags": list
        }
    """
    try:
        print(f"[Pipeline Step 3] Generating content with Qwen-Flash LLM...")
        
        if not DASHSCOPE_API_KEY or DASHSCOPE_API_KEY == "your_dashscope_api_key_here":
            raise ValueError("DASHSCOPE_API_KEY not configured in .env file")
        
        # Initialize OpenAI client with DashScope endpoint
        client = OpenAI(
            api_key=DASHSCOPE_API_KEY,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
        )
        
        # Prepare product information for prompt
        niche = product_attributes["niche"]["name"]
        labels = ", ".join(product_attributes["labels"][:8])
        price = price_data["estimated_price"]
        
        # Construct prompt
        system_prompt = """You are an expert marketplace SEO specialist. Generate compelling, SEO-optimized product listings that drive conversions.
Your listings should be:
- Engaging and benefit-focused
- Keyword-rich for search optimization
- Professional yet persuasive
- Formatted for marketplace platforms (eBay, Amazon, Mercado Livre)"""

        user_prompt = f"""Generate a complete product listing for a {niche} product with these details:

Product Category: {niche}
Detected Features: {labels}
Estimated Price: ${price} USD

Please provide:
1. A catchy, SEO-optimized product title (60-80 characters)
2. A compelling product description (150-200 words)
3. 5 bullet points highlighting key features and benefits
4. 8-10 relevant search tags/keywords

Format your response as JSON with keys: title, description, bullet_points, tags"""

        # Call Qwen-Flash API
        response = client.chat.completions.create(
            model="qwen-flash",  # Free, fast model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Parse response
        generated_text = response.choices[0].message.content
        
        # Try to extract JSON from response
        try:
            # Find JSON in response (may be wrapped in markdown code blocks)
            if "```json" in generated_text:
                json_start = generated_text.find("```json") + 7
                json_end = generated_text.find("```", json_start)
                json_text = generated_text[json_start:json_end].strip()
            elif "```" in generated_text:
                json_start = generated_text.find("```") + 3
                json_end = generated_text.find("```", json_start)
                json_text = generated_text[json_start:json_end].strip()
            else:
                json_text = generated_text
            
            result = json.loads(json_text)
        except json.JSONDecodeError:
            # Fallback if LLM doesn't return valid JSON
            result = {
                "title": f"Premium {niche} Product - High Quality",
                "description": generated_text[:500],
                "bullet_points": [
                    f"Category: {niche}",
                    f"Features: {labels}",
                    f"Estimated value: ${price}",
                    "Fast shipping available",
                    "Quality guaranteed"
                ],
                "tags": product_attributes["labels"][:8]
            }
        
        print(f"[Pipeline Step 3] ✓ Content generated: {result['title'][:50]}...")
        return result
        
    except Exception as e:
        print(f"[Pipeline Step 3] ✗ Error: {str(e)}")
        # Return fallback content on error
        return {
            "title": f"{product_attributes['niche']['name']} Product",
            "description": f"High-quality {product_attributes['niche']['name']} product. {', '.join(product_attributes['labels'][:5])}.",
            "bullet_points": [f"Feature: {label}" for label in product_attributes['labels'][:5]],
            "tags": product_attributes['labels'][:8],
            "error": str(e)
        }


async def generate_3d_assets(image_path: str) -> Dict[str, Any]:
    """
    Step 4: Generate multi-format 3D assets from product image
    Uses Trellis to generate GLB, then converts to MP4 and USDZ
    
    Pipeline:
    1. Pre-process: Remove background
    2. Call Trellis API → GLB + preview renders
    3. Download GLB (async streaming)
    4. Parallel conversions: GLB → MP4 + GLB → USDZ
    
    Args:
        image_path: Path to the product image
        
    Returns:
        dict: {
            "glb_path": str | None,
            "mp4_path": str | None,
            "usdz_path": str | None,
            "preview_renders": list[str],
            "preprocessed_image_path": str,
            "status": str,
            "processing_time": float,
            "formats_generated": list[str]
        }
    """
    import time
    import uuid
    from tenacity import retry, stop_after_attempt, wait_exponential
    from backend.converters import download_file_streaming, glb_to_mp4_simple
    from backend.converters.glb_to_usdz import glb_to_usdz_simple
    
    start_time = time.time()
    
    try:
        print(f"[Pipeline Step 4] Generating 3D assets with Trellis...")
        
        # [STEP 1] Pre-processing: Remove background
        print(f"[Pipeline Step 4] Pre-processing: Removing background...")
        with open(image_path, 'rb') as f:
            input_image = f.read()
        
        # Remove background using rembg
        output_image = remove(input_image)
        
        # Convert to PIL Image and add white background
        img = Image.open(BytesIO(output_image)).convert("RGBA")
        
        # Create white background
        white_bg = Image.new("RGB", img.size, (255, 255, 255))
        white_bg.paste(img, mask=img.split()[3])  # Use alpha channel as mask
        
        # Save preprocessed image
        preprocessed_path = image_path.replace(".jpg", "_processed.png").replace(".jpeg", "_processed.png")
        white_bg.save(preprocessed_path, "PNG")
        print(f"[Pipeline Step 4] ✓ Background removed: {preprocessed_path}")
        
        # [STEP 2] Check if Replicate token is configured
        if not REPLICATE_API_TOKEN or REPLICATE_API_TOKEN == "your_replicate_api_token_here":
            print(f"[Pipeline Step 4] ⚠ REPLICATE_API_TOKEN not configured")
            return {
                "glb_path": None,
                "mp4_path": None,
                "usdz_path": None,
                "preview_renders": [],
                "preprocessed_image_path": preprocessed_path,
                "status": "skipped",
                "message": "Replicate API token not configured. 3D generation skipped.",
                "processing_time": time.time() - start_time,
                "formats_generated": []
            }
        
        # [STEP 3] Call Trellis API with retry logic
        print(f"[Pipeline Step 4] Calling Trellis API...")
        
        # Read preprocessed image and convert to base64
        with open(preprocessed_path, 'rb') as f:
            image_data = f.read()
            image_b64 = base64.b64encode(image_data).decode()
        
        @retry(
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=2, max=10)
        )
        def call_trellis_with_retry():
            return replicate.run(
                "firtoz/trellis:e8f6c45206993f297372f5436b90350817bd9b4a0d52d2a76df50c1c8afa2b3c",
                input={
                    "image": f"data:image/png;base64,{image_b64}",
                    "seed": 0,
                    "texture_size": 1024,
                    "mesh_simplify": 0.95,
                    "generate_model": True,
                    "generate_color": True,
                    "generate_normal": True,
                    "ss_sampling_steps": 12,
                    "slat_sampling_steps": 12,
                    "ss_guidance_strength": 7.5,
                    "slat_guidance_strength": 3
                }
            )
        
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        trellis_output = await loop.run_in_executor(None, call_trellis_with_retry)
        
        print(f"[Pipeline Step 4] ✓ Trellis API complete")
        
        # [STEP 4] Parse Trellis output
        glb_url = None
        preview_urls = []
        
        if isinstance(trellis_output, dict):
            glb_url = trellis_output.get("model")
            # Collect preview renders
            for key, value in trellis_output.items():
                if key.startswith("render_") and value:
                    preview_urls.append(value)
        elif isinstance(trellis_output, str):
            glb_url = trellis_output
        
        if not glb_url:
            raise ValueError("Trellis did not return a valid GLB model URL")
        
        # [STEP 5] Download GLB (async streaming)
        print(f"[Pipeline Step 4] Downloading GLB model...")
        glb_filename = f"{uuid.uuid4().hex[:8]}.glb"
        glb_path = f"data/models/{glb_filename}"
        
        glb_path = await download_file_streaming(glb_url, glb_path)
        
        # [STEP 6] Parallel conversions: GLB → MP4 + GLB → USDZ
        print(f"[Pipeline Step 4] Converting to multiple formats...")
        
        mp4_path = glb_path.replace(".glb", ".mp4")
        usdz_path = glb_path.replace(".glb", ".usdz")
        
        # Run conversions in parallel with graceful degradation
        mp4_task = glb_to_mp4_simple(glb_path, mp4_path)
        usdz_task = glb_to_usdz_simple(glb_path, usdz_path)
        
        conversion_results = await asyncio.gather(
            mp4_task,
            usdz_task,
            return_exceptions=True  # Don't fail if one conversion fails
        )
        
        # Parse results
        mp4_result = conversion_results[0]
        usdz_result = conversion_results[1]
        
        # Check which conversions succeeded
        formats_generated = ["glb"]
        
        if not isinstance(mp4_result, Exception):
            mp4_path = mp4_result
            formats_generated.append("mp4")
            print(f"[Pipeline Step 4] ✓ MP4 generated: {mp4_path}")
        else:
            print(f"[Pipeline Step 4] ⚠ MP4 conversion failed: {mp4_result}")
            mp4_path = None
        
        if usdz_result and not isinstance(usdz_result, Exception):
            usdz_path = usdz_result
            formats_generated.append("usdz")
            print(f"[Pipeline Step 4] ✓ USDZ generated: {usdz_path}")
        else:
            if isinstance(usdz_result, Exception):
                print(f"[Pipeline Step 4] ⚠ USDZ conversion failed: {usdz_result}")
            else:
                print(f"[Pipeline Step 4] ⚠ USDZ conversion skipped (MVP)")
            usdz_path = None
        
        # [STEP 7] Prepare result
        processing_time = time.time() - start_time
        
        result = {
            "glb_path": glb_path,
            "mp4_path": mp4_path,
            "usdz_path": usdz_path,
            "preview_renders": preview_urls,
            "preprocessed_image_path": preprocessed_path,
            "status": "completed",
            "processing_time": round(processing_time, 2),
            "formats_generated": formats_generated
        }
        
        print(f"[Pipeline Step 4] ✓ 3D assets generated in {processing_time:.1f}s")
        print(f"[Pipeline Step 4] Formats: {', '.join(formats_generated)}")
        
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        print(f"[Pipeline Step 4] ✗ Error: {str(e)}")
        
        # Return partial results if available
        return {
            "glb_path": glb_path if 'glb_path' in locals() else None,
            "mp4_path": None,
            "usdz_path": None,
            "preview_renders": preview_urls if 'preview_urls' in locals() else [],
            "preprocessed_image_path": preprocessed_path if 'preprocessed_path' in locals() else None,
            "status": "error",
            "error": str(e),
            "processing_time": round(processing_time, 2),
            "formats_generated": []
        }


async def export_listing(all_pipeline_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 5: Export complete listing in marketplace-ready formats
    
    Args:
        all_pipeline_data: Combined output from all pipeline steps
        
    Returns:
        dict: {
            "listing_id": str,
            "export_formats": dict,
            "files": dict
        }
    """
    try:
        print(f"[Pipeline Step 5] Exporting listing data...")
        
        import uuid
        listing_id = str(uuid.uuid4())
        
        # Create marketplace-specific exports
        export_formats = {
            "ebay": {
                "title": all_pipeline_data["content"]["title"],
                "description": all_pipeline_data["content"]["description"],
                "category": all_pipeline_data["image_analysis"]["niche"]["name"],
                "price": all_pipeline_data["price"]["estimated_price"],
                "condition": "New",
                "listing_type": "FixedPrice",
                "media": {
                    "video": all_pipeline_data["assets_3d"].get("mp4_path"),
                    "images": all_pipeline_data["assets_3d"].get("preview_renders", [])
                }
            },
            "amazon": {
                "product_name": all_pipeline_data["content"]["title"],
                "description": all_pipeline_data["content"]["description"],
                "bullet_points": all_pipeline_data["content"]["bullet_points"],
                "keywords": all_pipeline_data["content"]["tags"],
                "price": all_pipeline_data["price"]["estimated_price"],
                "media": {
                    "3d_model": all_pipeline_data["assets_3d"].get("glb_path"),  # Amazon supports GLB
                    "video": all_pipeline_data["assets_3d"].get("mp4_path"),
                    "images": all_pipeline_data["assets_3d"].get("preview_renders", [])
                }
            },
            "mercado_livre": {
                "titulo": all_pipeline_data["content"]["title"],
                "descricao": all_pipeline_data["content"]["description"],
                "categoria": all_pipeline_data["image_analysis"]["niche"]["name"],
                "preco": all_pipeline_data["price"]["estimated_price"],
                "moeda": "USD",
                "midia": {
                    "video": all_pipeline_data["assets_3d"].get("mp4_path"),
                    "imagens": all_pipeline_data["assets_3d"].get("preview_renders", [])
                }
            }
        }
        
        # Save export data
        export_file = f"data/exports/listing_{listing_id}.json"
        os.makedirs("data/exports", exist_ok=True)
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump({
                "listing_id": listing_id,
                "pipeline_data": all_pipeline_data,
                "exports": export_formats
            }, f, indent=2, ensure_ascii=False)
        
        result = {
            "listing_id": listing_id,
            "export_formats": export_formats,
            "files": {
                "json": export_file,
                "glb_3d_model": all_pipeline_data["assets_3d"].get("glb_path"),
                "mp4_video": all_pipeline_data["assets_3d"].get("mp4_path"),
                "usdz_ar_model": all_pipeline_data["assets_3d"].get("usdz_path"),
                "preview_renders": all_pipeline_data["assets_3d"].get("preview_renders", []),
                "processed_image": all_pipeline_data["assets_3d"].get("preprocessed_image_path")
            }
        }
        
        print(f"[Pipeline Step 5] ✓ Listing exported: {listing_id}")
        return result
        
    except Exception as e:
        print(f"[Pipeline Step 5] ✗ Error: {str(e)}")
        raise

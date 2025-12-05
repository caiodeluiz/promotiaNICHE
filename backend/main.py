from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Dict
from pathlib import Path

load_dotenv()
from fastapi.staticfiles import StaticFiles

# Import auth and database
from backend.auth import get_current_user
import backend.user_db as user_db # Assuming user_db module contains db operations
from backend.database import init_db, get_db_connection
from backend.vision import detect_labels
from backend.classifier import classify_product

# Import pipeline steps
from backend.pipeline_steps import (
    analyze_image,
    research_price,
    generate_content,
    generate_3d_assets,
    export_listing
)

import shutil
import os
import json
import uuid
import asyncio

app = FastAPI(title="Listify Pipeline")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust this to your frontend's origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')

@app.get("/style.css")
async def read_css():
    return FileResponse('frontend/style.css')

@app.get("/script.js")
async def read_js():
    return FileResponse('frontend/script.js')

@app.on_event("startup")
async def startup_event():
    init_db()

class FeedbackRequest(BaseModel):
    history_id: int
    feedback: str
    corrected_niche_id: int = None

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/niches")
async def get_niches():
    conn = get_db_connection()
    niches = conn.execute("SELECT * FROM niches").fetchall()
    conn.close()
    return [{"id": n["id"], "name": n["name"]} for n in niches]

@app.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload endpoint to generate 3D assets and listing copy (requires authentication)"""
    print("\n" + "="*80)
    print("LISTIFY PIPELINE STARTED")
    print("="*80)
    
    try:
        user_id = current_user["id"]
        user_email = current_user["email"]
        
        # Check if user has credits
        user_data = user_db.get_user_by_id(user_id)
        if not user_data or user_data["credits"] < 1:
            raise HTTPException(
                status_code=402,
                detail="Insufficient credits. Please purchase more credits to continue."
            )
        
        # Deduct credit
        if not user_db.deduct_credits(user_id, amount=1):
            raise HTTPException(status_code=402, detail="Failed to deduct credits")
        
        # Generate unique listing ID
        listing_id = str(uuid.uuid4())
        
        # Save file to disk
        file_ext = file.filename.split(".")[-1]
        filename = f"{uuid.uuid4()}.{file_ext}"
        filepath = f"data/{filename}"
        
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"✓ Image uploaded: {filepath}")
        
        # STEP 1: Analyze Image
        image_analysis = await analyze_image(filepath)
        
        # STEP 2: Research Price
        price_data = await research_price(image_analysis)
        
        # STEP 3: Generate Content (Qwen-Flash LLM)
        content_data = await generate_content(image_analysis, price_data)
        
        # STEP 4: Generate 3D Assets (Trellis → GLB + MP4 + USDZ)
        assets_data = await generate_3d_assets(filepath)
        
        # STEP 5: Export Listing
        pipeline_output = {
            "image_analysis": image_analysis,
            "price": price_data,
            "content": content_data,
            "assets_3d": assets_data
        }
        export_data = await export_listing(pipeline_output)
        
        # Save to database (for history/feedback)
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO products (image_path) VALUES (?)", (filepath,))
        product_id = cursor.lastrowid
        
        cursor.execute(
            "INSERT INTO history (product_id, niche_id, confidence, labels) VALUES (?, ?, ?, ?)",
            (product_id, image_analysis["niche"]["id"], image_analysis["confidence"], json.dumps(image_analysis["labels"]))
        )
        history_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        print("="*80)
        print("LISTIFY PIPELINE COMPLETED SUCCESSFULLY")
        print("="*80 + "\n")
        
        # Return complete pipeline result
        # Get results
        result = {
            "listing_id": listing_id,
            "export_formats": export_data, # Assuming export_data is the export_result
            "files": {
                "json": None, # Placeholder, as export_listing doesn't return a path directly
                "glb_3d_model": assets_data.get("glb_path"),
                "mp4_video": assets_data.get("mp4_path"),
                "usdz_ar_model": assets_data.get("usdz_path"),
                "preview_renders": assets_data.get("preview_renders", []),
                "processed_image": filepath # Using the original uploaded filepath
            }
        }
        
        # Save listing to database
        try:
            amazon_format = export_data.get("amazon", {})
            user_db.db.save_listing(
                user_id=user_id,
                image_url=str(result["files"]["processed_image"]),
                title=amazon_format.get("product_name", "Generated Product"),
                description=amazon_format.get("description", ""),
                glb_url=str(result["files"]["glb_3d_model"]) if result["files"]["glb_3d_model"] else None,
                mp4_url=str(result["files"]["mp4_video"]) if result["files"]["mp4_video"] else None,
                usdz_url=str(result["files"]["usdz_ar_model"]) if result["files"]["usdz_ar_model"] else None,
                price=str(amazon_format.get("price", "")),
                keywords=json.dumps(amazon_format.get("keywords", [])),
            )
        except Exception as db_error:
            print(f"Warning: Failed to save listing to database: {db_error}")
        
        return JSONResponse(content=result)
        
    except HTTPException:
        # Re-raise HTTP exceptions (auth errors, insufficient credits)
        raise
    except Exception as e:
        # Refund credit on error
        try:
            user_db.refund_credits(user_id, amount=1, reason=f"Generation failed: {str(e)}")
        except:
            pass
        
        print(f"Error processing upload: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to process image: {str(e)}")

@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE history SET feedback = ?, niche_id = COALESCE(?, niche_id) WHERE id = ?",
        (feedback.feedback, feedback.corrected_niche_id, feedback.history_id)
    )
    
    # Learning Logic
    if feedback.corrected_niche_id:
        # Get labels from history
        row = cursor.execute("SELECT labels FROM history WHERE id = ?", (feedback.history_id,)).fetchone()
        if row and row["labels"]:
            labels = json.loads(row["labels"])
            
            # Add labels to keywords table for the corrected niche
            for label in labels:
                # Check if keyword already exists for this niche to avoid duplicates (optional but good)
                exists = cursor.execute(
                    "SELECT 1 FROM keywords WHERE niche_id = ? AND keyword = ?", 
                    (feedback.corrected_niche_id, label)
                ).fetchone()
                
                if not exists:
                    cursor.execute(
                        "INSERT INTO keywords (niche_id, keyword, weight) VALUES (?, ?, ?)", 
                        (feedback.corrected_niche_id, label, 2.0) # Give learned keywords higher weight
                    )
                    print(f"LEARNED: Added '{label}' to niche {feedback.corrected_niche_id}")

    conn.commit()
    conn.close()
    
    return {"status": "feedback recorded and learning updated"}


# ============================================================================
# PAYMENT ENDPOINTS (Phase 7: Stripe Integration)
# ============================================================================

from backend.payments import (
    create_checkout_session,
    verify_webhook_signature,
    process_successful_payment,
    get_all_packages
)
from fastapi import Header, Request


class CreateCheckoutRequest(BaseModel):
    package_id: str


@app.get("/payments/packages")
async def get_credit_packages():
    """Get all available credit packages."""
    return get_all_packages()


@app.post("/payments/create-checkout-session")
async def create_stripe_checkout(
    request: CreateCheckoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Create a Stripe Checkout session for credit purchase.
    Requires authentication.
    """
    try:
        user_id = current_user["id"]
        user_email = current_user["email"]
        
        # Create Stripe Checkout session
        session_data = create_checkout_session(
            package_id=request.package_id,
            user_id=user_id,
            user_email=user_email
        )
        
        return session_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")


@app.post("/payments/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature")
):
    """
    Stripe webhook endpoint to handle payment events.
    This endpoint is called by Stripe when payments are completed.
    """
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")
    
    try:
        # Get raw body
        payload = await request.body()
        
        # Verify webhook signature
        event = verify_webhook_signature(payload, stripe_signature)
        
        # Handle checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            
            # Extract payment information
            payment_info = process_successful_payment(session)
            
            # Add credits to user
            success = user_db.db.add_credits_from_payment(
                user_id=payment_info['user_id'],
                credits=payment_info['credits'],
                stripe_session_id=payment_info['stripe_session_id'],
                package_id=payment_info['package_id'],
                amount_paid=payment_info['amount_paid']
            )
            
            if success:
                print(f"✓ Credits added: {payment_info['credits']} credits to user {payment_info['user_id']}")
            else:
                print(f"⚠ Payment already processed: {payment_info['stripe_session_id']}")
        
        return {"status": "success"}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

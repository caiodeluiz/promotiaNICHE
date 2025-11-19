from fastapi import FastAPI, UploadFile, File, HTTPException
from dotenv import load_dotenv

load_dotenv()
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.database import init_db, get_db_connection
from backend.vision import detect_labels
from backend.classifier import classify_product
import shutil
import os
import json
import uuid

app = FastAPI(title="Promotia Niche Classifier")

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
async def upload_image(file: UploadFile = File(...)):
    # Save file to disk
    file_ext = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{file_ext}"
    filepath = f"data/{filename}"
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Detect labels
    try:
        labels = detect_labels(filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    # Classify
    result = classify_product(labels)
    
    # Save to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("INSERT INTO products (image_path) VALUES (?)", (filepath,))
    product_id = cursor.lastrowid
    
    cursor.execute(
        "INSERT INTO history (product_id, niche_id, confidence, labels) VALUES (?, ?, ?, ?)",
        (product_id, result["niche_id"], result["confidence"], json.dumps(labels))
    )
    history_id = cursor.lastrowid
    
    conn.commit()
    conn.close()
    
    return {
        "history_id": history_id,
        "product_id": product_id,
        "labels": labels,
        "classification": result
    }

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

from backend.database import get_db_connection

def classify_product(labels: list[str]) -> dict:
    """
    Classifies a product into a niche based on detected labels.
    Returns a dictionary with the niche name and confidence score.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get all keywords and their associated niches
    cursor.execute("SELECT k.keyword, k.weight, n.id as niche_id, n.name as niche_name FROM keywords k JOIN niches n ON k.niche_id = n.id")
    keywords_db = cursor.fetchall()
    
    niche_scores = {}
    
    for label in labels:
        for row in keywords_db:
            # Simple partial match
            if row['keyword'] in label or label in row['keyword']:
                niche_id = row['niche_id']
                niche_name = row['niche_name']
                weight = row['weight']
                
                if niche_id not in niche_scores:
                    niche_scores[niche_id] = {"name": niche_name, "score": 0}
                
                niche_scores[niche_id]["score"] += weight

    conn.close()

    if not niche_scores:
        return {"niche": "Unknown", "confidence": 0.0, "niche_id": None}

    # Find the niche with the highest score
    best_niche_id = max(niche_scores, key=lambda k: niche_scores[k]["score"])
    best_niche = niche_scores[best_niche_id]
    
    # Normalize score (simple heuristic)
    total_score = sum(n["score"] for n in niche_scores.values())
    confidence = best_niche["score"] / total_score if total_score > 0 else 0.0
    
    return {
        "niche": best_niche["name"],
        "confidence": round(confidence, 2),
        "niche_id": best_niche_id
    }

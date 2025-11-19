from backend.database import get_db_connection, init_db
import os

def seed_data():
    # Reset database
    if os.path.exists("data/promotia.db"):
        os.remove("data/promotia.db")
    
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    niches = [
        ("Fitness & Wellness", "Yoga, gym, workout gear, supplements, health."),
        ("Pet Supplies", "Toys, food, accessories for dogs, cats, and other pets."),
        ("Home Office", "Desks, chairs, computers, productivity tools."),
        ("Beauty & Personal Care", "Makeup, skincare, grooming, bath products."),
        ("Tech Accessories", "Phone cases, chargers, cables, gadgets."),
        ("Outdoor & Adventure", "Camping gear, hiking equipment, travel essentials."),
        ("Kitchen & Dining", "Cookware, utensils, appliances, tableware."),
        ("Fashion & Apparel", "Clothing, shoes, accessories, style."),
        ("Gaming", "Consoles, controllers, headsets, video games."),
        ("Home Decor", "Furniture, lighting, rugs, decoration."),
        ("Baby & Kids", "Toys, diapers, strollers, baby care."),
        ("Automotive", "Car accessories, tools, maintenance."),
        ("Gardening", "Plants, tools, seeds, outdoor living."),
        ("Books & Media", "Books, vinyl, movies, music."),
        ("Art & Crafts", "Paint, brushes, yarn, DIY supplies.")
    ]

    for name, desc in niches:
        try:
            cursor.execute("INSERT INTO niches (name, description) VALUES (?, ?)", (name, desc))
            niche_id = cursor.lastrowid
            
            # Add keywords for each niche
            keywords = []
            if name == "Fitness & Wellness":
                keywords = ["yoga", "gym", "dumbbell", "mat", "protein", "workout", "sport", "run", "fitness", "exercise"]
            elif name == "Pet Supplies":
                keywords = ["dog", "cat", "pet", "toy", "food", "leash", "collar", "animal", "puppy", "kitten"]
            elif name == "Home Office":
                keywords = ["desk", "chair", "computer", "laptop", "monitor", "keyboard", "mouse", "office", "work"]
            elif name == "Beauty & Personal Care":
                keywords = ["makeup", "lipstick", "cream", "skin", "hair", "brush", "perfume", "soap", "lotion"]
            elif name == "Tech Accessories":
                keywords = ["phone", "case", "charger", "cable", "usb", "headphone", "earbud", "battery", "screen"]
            elif name == "Outdoor & Adventure":
                keywords = ["tent", "backpack", "hike", "camp", "sleeping", "boot", "compass", "map", "nature"]
            elif name == "Kitchen & Dining":
                keywords = ["pan", "pot", "knife", "spoon", "fork", "plate", "bowl", "cup", "mug", "chef"]
            elif name == "Fashion & Apparel":
                keywords = ["shirt", "pants", "dress", "shoe", "hat", "jacket", "jeans", "clothing", "wear"]
            elif name == "Gaming":
                keywords = ["game", "console", "controller", "joystick", "headset", "xbox", "playstation", "nintendo"]
            elif name == "Home Decor":
                keywords = ["sofa", "lamp", "rug", "vase", "pillow", "curtain", "mirror", "furniture", "room"]
            elif name == "Baby & Kids":
                keywords = ["baby", "diaper", "toy", "stroller", "crib", "bottle", "pacifier", "kid", "child"]
            elif name == "Automotive":
                keywords = ["car", "tire", "wheel", "oil", "tool", "vehicle", "auto", "drive"]
            elif name == "Gardening":
                keywords = ["plant", "flower", "garden", "shovel", "pot", "soil", "seed", "grow", "green"]
            elif name == "Books & Media":
                keywords = ["book", "novel", "read", "vinyl", "record", "music", "movie", "cd", "paper"]
            elif name == "Art & Crafts":
                keywords = ["paint", "brush", "canvas", "draw", "pencil", "yarn", "knit", "craft", "art"]
            
            for kw in keywords:
                cursor.execute("INSERT INTO keywords (niche_id, keyword) VALUES (?, ?)", (niche_id, kw))
                
        except Exception as e:
            print(f"Skipping {name}: {e}")

    conn.commit()
    conn.close()
    print("Database reset and seeded with Expanded Marketing Niches successfully.")

if __name__ == "__main__":
    seed_data()

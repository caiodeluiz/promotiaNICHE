"""
Database models and utilities for user management.
This module provides a bridge between the Python backend and the Next.js Prisma database.
"""
import os
import sqlite3
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

# Path to the Next.js Prisma database
DB_PATH = Path(__file__).parent.parent.parent / "frontend-next" / "dev.db"


class UserDatabase:
    """Interface to interact with the Next.js user database."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
    
    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, email, name, credits, createdAt FROM User WHERE email = ?",
                (email,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        conn = self.get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT id, email, name, credits, createdAt FROM User WHERE id = ?",
                (user_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def deduct_credits(self, user_id: str, amount: int = 1) -> bool:
        """
        Deduct credits from a user.
        Returns True if successful, False if insufficient credits.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check current credits
            cursor.execute("SELECT credits FROM User WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            if not row or row[0] < amount:
                return False
            
            # Deduct credits
            cursor.execute(
                "UPDATE User SET credits = credits - ? WHERE id = ?",
                (amount, user_id)
            )
            
            # Log transaction
            cursor.execute(
                """INSERT INTO Transaction (id, userId, type, amount, description, createdAt)
                   VALUES (?, ?, 'deduction', ?, 'Image upload and 3D generation', ?)""",
                (self._generate_cuid(), user_id, -amount, datetime.utcnow().isoformat())
            )
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def refund_credits(self, user_id: str, amount: int = 1, reason: str = "Generation failed"):
        """Refund credits to a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE User SET credits = credits + ? WHERE id = ?",
                (amount, user_id)
            )
            
            # Log transaction
            cursor.execute(
                """INSERT INTO Transaction (id, userId, type, amount, description, createdAt)
                   VALUES (?, ?, 'refund', ?, ?, ?)""",
                (self._generate_cuid(), user_id, amount, reason, datetime.utcnow().isoformat())
            )
            
            conn.commit()
        finally:
            conn.close()
    
    def save_listing(
        self,
        user_id: str,
        image_url: str,
        title: str,
        description: str,
        glb_url: Optional[str] = None,
        mp4_url: Optional[str] = None,
        usdz_url: Optional[str] = None,
        price: Optional[str] = None,
        keywords: str = "[]",
    ) -> str:
        """Save a listing to the database. Returns listing ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            listing_id = self._generate_cuid()
            cursor.execute(
                """INSERT INTO Listing 
                   (id, userId, imageUrl, title, description, glbUrl, mp4Url, usdzUrl, price, keywords, creditsUsed, createdAt)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1, ?)""",
                (
                    listing_id,
                    user_id,
                    image_url,
                    title,
                    description,
                    glb_url,
                    mp4_url,
                    usdz_url,
                    price,
                    keywords,
                    datetime.utcnow().isoformat(),
                )
            )
            conn.commit()
            return listing_id
        finally:
            conn.close()
    
    def add_credits_from_payment(
        self,
        user_id: str,
        credits: int,
        stripe_session_id: str,
        package_id: str,
        amount_paid: float
    ) -> bool:
        """
        Add credits to user from a successful Stripe payment.
        Implements idempotency to prevent duplicate credit additions.
        
        Args:
            user_id: User's ID
            credits: Number of credits to add
            stripe_session_id: Stripe checkout session ID
            package_id: Package identifier
            amount_paid: Amount paid in dollars
            
        Returns:
            True if credits were added, False if already processed
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if this payment was already processed (idempotency)
            cursor.execute(
                "SELECT id FROM Transaction WHERE stripeId = ?",
                (stripe_session_id,)
            )
            if cursor.fetchone():
                return False  # Already processed
            
            # Add credits to user
            cursor.execute(
                "UPDATE User SET credits = credits + ? WHERE id = ?",
                (credits, user_id)
            )
            
            # Log transaction
            description = f"Purchased {package_id} pack: {credits} credits (${amount_paid:.2f})"
            cursor.execute(
                """INSERT INTO Transaction (id, userId, type, amount, stripeId, description, createdAt)
                   VALUES (?, ?, 'purchase', ?, ?, ?, ?)""",
                (
                    self._generate_cuid(),
                    user_id,
                    credits,
                    stripe_session_id,
                    description,
                    datetime.utcnow().isoformat()
                )
            )
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def _generate_cuid() -> str:
        """Generate a simple unique ID (simplified version of cuid)."""
        import time
        import random
        import string
        
        timestamp = hex(int(time.time() * 1000))[2:]
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
        return f"c{timestamp}{random_part}"


# Singleton instance
db = UserDatabase()

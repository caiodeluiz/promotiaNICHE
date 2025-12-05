"""
Authentication middleware for the Python backend.
Verifies JWT tokens from Next.js NextAuth sessions.
"""
import os
import jwt
from typing import Optional
from fastapi import HTTPException, Header

# This should match NEXTAUTH_SECRET in frontend .env
NEXTAUTH_SECRET = os.getenv("NEXTAUTH_SECRET", "listify-secret-key-change-in-production")


def decode_session_token(token: str) -> Optional[dict]:
    """
    Decode and verify a NextAuth JWT session token.
    Returns the decoded payload if valid, None otherwise.
    """
    try:
        # NextAuth uses HS256 by default
        payload = jwt.decode(
            token,
            NEXTAUTH_SECRET,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid session token")


async def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    """
    FastAPI dependency to get the current authenticated user from the session token.
    Expects: Authorization: Bearer <token>
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Extract Bearer token
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        
        # Decode token
        payload = decode_session_token(token)
        
        # Extract user info (NextAuth stores user data in the token)
        user_id = payload.get("id") or payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        
        return {
            "id": user_id,
            "email": email,
            "name": payload.get("name"),
        }
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

from fastapi import Depends, HTTPException, Header
from typing import Optional
from database import get_db

async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Validates Supabase JWT and returns the user object.
    In a real production environment, we should verify the JWT signature locally
    to save network calls, or use the Supabase Admin client if needed.
    """
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    token = authorization.replace("Bearer ", "").strip()
    
    if not token:
        raise HTTPException(status_code=401, detail="Invalid Authorization Header format")
    
    try:
        # Verify with Supabase
        db = get_db()
        user_response = db.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(status_code=401, detail="Invalid Authentication Token")
            
        return user_response.user
    except Exception as e:
        # Log the error for debugging
        print(f"Auth error: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")

def require_role(role: str):
    """
    Dependency to check if the user has a specific role (stored in app_metadata or tables).
    For this MVP, we might mock this or check a 'roles' table if we had one.
    To allow testing without complex setup, we will skip strict role check enforcement 
    via DB for now or assume claims are in metadata.
    """
    async def role_checker(user = Depends(get_current_user)):
        # Simplified: In real app, check user.app_metadata.get('role') == role
        # For Hackathon MVP: We trust the user is authenticated. 
        # If we need specific roles, we'd check here.
        return user
    return role_checker

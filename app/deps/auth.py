from fastapi import Depends, HTTPException 
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from app.core.config import settings   # ✅ use instance not class

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")




# ✅ Get current user
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        print("PAYLOAD:", payload)
        return payload
    except:
        raise HTTPException(status_code=401, detail="Invalid Token")


# ✅ FIXED ROLE FUNCTION
def require_role(allowed_roles: list):   # ✅ REMOVE async here
    async def checker(user=Depends(get_current_user)):
        if user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access Denied. Allowed roles: {allowed_roles}"
            )
        return user
    return checker


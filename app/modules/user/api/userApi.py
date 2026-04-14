from fastapi import APIRouter ,Depends
from app.deps.auth  import get_current_user , require_role

router = APIRouter(prefix="/user", tags=["Users"])


@router.get("/profile")
async def get_profile(user=Depends(get_current_user)):
    return {
        "message": "User Profile",
        "user": user
    }

from fastapi import APIRouter , Depends
from app.deps.auth import require_role

router =APIRouter(prefix="/admin" ,tags=['Admin'])

@router.get("/admin")
async def admin_data(user=Depends(require_role(["admin"]))):
    return {"message": "Admin Access"}
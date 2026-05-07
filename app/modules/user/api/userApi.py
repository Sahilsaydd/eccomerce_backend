from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.deps.db import get_db
from app.deps.auth import get_current_user
from app.modules.user.model.user import User

router = APIRouter(prefix="/user", tags=["Users"])


@router.get("/profile")
async def get_profile(
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user)
):
    try:
        user_id = user.get("sub")
        if not user_id:
             return {"error": "Invalid token payload"}
             
        result = await db.execute(select(User).where(User.id == int(user_id)))
        db_user = result.scalars().first()

        if not db_user:
            return {"error": "User not found"}

        return {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "role": db_user.role,
            "created_at": db_user.created_at
        }
    except Exception as e:
        print(f"ERROR in get_profile: {str(e)}")
        return {"error": str(e)}

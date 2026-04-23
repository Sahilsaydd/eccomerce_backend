from fastapi.security import OAuth2PasswordRequestForm 
from fastapi import APIRouter , Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps.db import get_db
from app.core.config import settings
from app.modules.auth.schemas.auth_schema import LogoutRequest, RegisterRequest, LoginRequest, AuthResponse
from app.modules.auth.services import auth_service
from app.deps.redis import get_redis, redis_client
from sqlalchemy.future import select
from app.utils.email import send_login_email , send_welcome_email
from app.modules.user.model.user import User
from jose import jwt

router =APIRouter(prefix="/auth", tags=["Auth"])

#  # backgroudtask  for register user email sending
# def send_welcome_email(email:str):
#     print(f"Welcome email sent to {email}")


# # background Task for login successfully 
# def log_login_activity(email:str):
#     print(f"User {email} Logged in successfully")


@router.post("/register")
async def register(
    data: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    #  Create user
    user = await auth_service.register_user(db, data)

    #  Send email in background (NO await)
    background_tasks.add_task(send_welcome_email, user)

    return {
        "message": "User registered successfully",
        "user_id": user.id
    }




@router.post("/login")
async def login(
    background_tasks: BackgroundTasks,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    data = LoginRequest(
        email=form_data.username,
        password=form_data.password
    )

    token_data = await auth_service.login_user(db, data)

    # Get user object from DB
    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Send email in background (NO await)
    background_tasks.add_task(send_login_email, user)

    return {
        "message": f"{user.name} Logged in successfully",
        "access_token": token_data["access_token"],
        "refresh_token": token_data["refresh_token"],
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(data: LogoutRequest):
    try:
        #  Decode token
        payload = jwt.decode(
            data.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        #  Check token type
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        #  Check if token exists in Redis
        stored = await redis_client.get(data.refresh_token)

        if not stored:
            raise HTTPException(status_code=401, detail="Token already expired")

        #  Delete token → LOGOUT
        await redis_client.delete(data.refresh_token)

        return {"message": "Logged out successfully"}

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")
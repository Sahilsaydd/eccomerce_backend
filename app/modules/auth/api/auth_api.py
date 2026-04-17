from fastapi.security import OAuth2PasswordRequestForm 
from fastapi import APIRouter , Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps.db import get_db
from app.modules.auth.schemas.auth_schema import RegisterRequest, LoginRequest, AuthResponse
from app.modules.auth.services import auth_service

from sqlalchemy.future import select
from app.utils.email import send_login_email , send_welcome_email
from app.modules.user.model.user import User


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

    token = await auth_service.login_user(db, data)

    #  Get user object from DB
    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    user = result.scalars().first()

    #  Send email in background (NO await)
    if user:
        background_tasks.add_task(send_login_email, user)

    return {
        "Massage": user.name + " "+"Logged in successfully",
        "access_token": token,
        "token_type": "bearer"
    }
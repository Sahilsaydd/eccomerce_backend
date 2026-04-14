from fastapi.security import OAuth2PasswordRequestForm 
from fastapi import APIRouter , Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps.db import get_db
from app.modules.auth.schemas.auth_schema import RegisterRequest, LoginRequest, AuthResponse
from app.modules.auth.services import auth_service

router =APIRouter(prefix="/auth", tags=["Auth"])

 # backgroudtask  for register user email sending
def send_welcome_email(email:str):
    print(f"Welcome email sent to {email}")


# background Task for login successfully 
def log_login_activity(email:str):
    print(f"User {email} Logged in successfully")


@router.post("/register")
async def register(data:RegisterRequest, BackgroundTasks: BackgroundTasks ,db:AsyncSession =Depends(get_db) ):
    BackgroundTasks.add_task(send_welcome_email, data.email)  # 👈 Schedule welcome email
    return await auth_service.register_user(db,data)



@router.post("/login")
async def login(BackgroundTasks: BackgroundTasks,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    data = LoginRequest(
        email=form_data.username,   # 👈 username becomes email
        password=form_data.password
    )

    token = await auth_service.login_user(db, data)

    BackgroundTasks.add_task(log_login_activity,data.email)  # 👈 Schedule login activity log

    return {
        "access_token": token,
        "token_type": "bearer"
    }
    
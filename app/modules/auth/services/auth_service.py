from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException , status
from app.modules.user.model.user import User
from app.core.security import hash_password ,verify_password ,create_access_token

async def register_user(db:AsyncSession ,data):
    result = await db.execute(select(User).where(User.email == data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400 , detail= "Email is Already Registered")
    
    user = User(
        name = data.name,
        email =data.email,
        password = hash_password(data.password),
        role = data.role

    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user



async def login_user(db:AsyncSession,data):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if(not user or not verify_password(data.password ,user.password)):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token(
        {
            "sub":user.email,
            "role":user.role
        }
    )
    return token


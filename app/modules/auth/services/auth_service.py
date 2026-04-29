from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException , status
from app.modules.user.model.user import User
from app.core.redis import redis_client

from app.core.security import hash_password ,verify_password ,create_access_token,create_refresh_token

async def register_user(db:AsyncSession ,data):
    result = await db.execute(select(User).where(User.email == data.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400 , detail= "Email is Already Registered")
    
    user = User(
        name = data.name,
        email =data.email,
        password = hash_password(data.password),
        role = data.role.value

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
            "sub": str(user.id), 
            "email": user.email,  
            "role": user.role
        }
    )

    refresh_token =create_refresh_token(
        {

        "sub": str(user.id)
        }
    )

    await redis_client.set(
        refresh_token,
        user.email,
        ex = 7 * 24*60*60
    )
    return {"access_token": token, "refresh_token": refresh_token , "role": user.role   }


async def get_userdetails(db:AsyncSession ,user_id:int):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    print("User Details:", user)
    if not user:
        raise HTTPException(status_code=404 , details="User Not Found")
    return user


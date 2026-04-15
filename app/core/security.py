import bcrypt
from jose import jwt
from datetime import datetime, timedelta
from app.core.config import settings


# Password hashing
def hash_password(password:str)->str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# Password verification
def verify_password(plain_password:str, hashed_password:str)->bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


# JWT token creation
def create_access_token(data:dict):
    to_encode = data.copy()
    expire = datetime.utcnow()+timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode , settings.SECRET_KEY, algorithm=settings.ALGORITHM)


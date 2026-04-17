from sqlalchemy import Column , Integer, String
from app.db.database import Base
from app.db.database import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    id = Column(Integer , primary_key=True , autoincrement=True , index=True)
    name= Column(String)
    email = Column(String ,unique=True)
    password = Column(String )
    role = Column(String)

    
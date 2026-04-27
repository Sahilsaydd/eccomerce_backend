from sqlalchemy import Column ,Integer ,String,ForeignKey,DateTime,Float
from sqlalchemy.sql import func
from app.db.database import Base
from app.db.database import BaseModel 

class Order(BaseModel):
    __tablename__ ="orders"
    id = Column(Integer ,primary_key=True , index=True)
    user_id = Column(Integer ,nullable=False)
    total_price = Column(Float, default=0)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=True)
    status = Column(String , default="Pending") # pending shipped deliverd
    created_at = Column(DateTime(timezone=True) ,server_default=func.now())

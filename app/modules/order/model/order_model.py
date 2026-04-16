from sqlalchemy import Column ,Integer ,String,ForeignKey,DateTime
from sqlalchemy.sql import func
from app.db.database import Base
 

class Order(Base):
    __tablename__ ="orders"
    id = Column(Integer ,primary_key=True , index=True)
    user_id = Column(Integer ,nullable=False)
    status = Column(String , default="Pending") # pending shipped deliverd
    created_at = Column(DateTime(timezone=True) ,server_default=func.now())

from sqlalchemy import Column , Integer ,String , Float , ForeignKey
from app.db.database import Base
from app.db.database import BaseModel
class OrderItems(BaseModel):
    __tablename__ ="order_items"
    
    id = Column(Integer , primary_key=True , index=True)
    order_id = Column(Integer , ForeignKey("orders.id"))
    product_id = Column(Integer)
    quantity = Column(Integer)
    price = Column(Float)
    
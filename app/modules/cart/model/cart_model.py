from sqlalchemy import Column, Integer , ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class  Cart(Base):
    __tablename__ ="carts"
    id = Column(Integer , primary_key=True ,index=True)
    user_id = Column(Integer , ForeignKey("users.id"), unique=True)
    items = relationship("CartItem",back_populates="cart",cascade="all,delete")


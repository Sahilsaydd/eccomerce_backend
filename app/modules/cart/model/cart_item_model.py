from sqlalchemy import Column , Integer ,ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base
from app.db.database import BaseModel
class CartItem(BaseModel):
    __tablename__ = "cart_items"

    id = Column(Integer,  primary_key=True, index=True)
    cart_id =Column(Integer ,ForeignKey("carts.id"))
    product_id = Column(Integer , ForeignKey("products.id"))
    quantity = Column(Integer , default=1)
    cart = relationship('Cart', back_populates="items")
       # 🔥 ADD THIS
    product = relationship("Product", back_populates="cart_items")
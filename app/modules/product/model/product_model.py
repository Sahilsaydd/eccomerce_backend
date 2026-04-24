from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.orm import relationship   # 👈 ADD THIS
from app.db.database import Base
from app.db.database import BaseModel
class Product(BaseModel):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    product_img = Column(String ,nullable=False)  
    rating = Column(Float, default=0.0)
   
    cart_items = relationship("CartItem", back_populates="product")
    
    stock = Column(Integer, default=0)
    brand = Column(String, nullable=True)
    discount_percentage = Column(Integer, default=0)
    product_images = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
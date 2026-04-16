from pydantic import BaseModel
from  typing import List

class OrderItemResponse(BaseModel):
    product_id:int 
    quantity:int
    price:float


class OrderResponse(BaseModel):
    id:int 
    user_id:int 
    status:str
    item: list[OrderItemResponse]

class OrderStatusUpdate(BaseModel):
    status:str



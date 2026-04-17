from pydantic import BaseModel, Field, field_validator
from  typing import List

class OrderItemResponse(BaseModel):
    product_id:int = Field(gt=0)
    quantity:int = Field(gt=0)
    price:float = Field(gt=0)


class OrderResponse(BaseModel):
    id:int 
    user_id:int 
    status:str
    item: list[OrderItemResponse]

class OrderStatusUpdate(BaseModel):
    status:str 
    @field_validator("status")
    def validate_status(cls, value):
        allowed = ["pending", "shipped", "delivered", "cancelled"]
        if value not in allowed:
            raise ValueError(f"Status must be one of {allowed}")
        return value


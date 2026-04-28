from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from decimal import Decimal
from enum import Enum


class OrderItemResponse(BaseModel):
    product_id: int = Field(..., gt=0, description="Product ID must be a positive integer")
    quantity: int = Field(..., gt=0, description="Quantity must be greater than 0")
    price: Decimal = Field(..., gt=0, description="Price must be a positive number")

    @field_validator("price")
    def validate_price(cls, value: Decimal):
        if value.as_tuple().exponent < -2:  # max 2 decimal places
            raise ValueError("Price must not have more than 2 decimal places")
        return value


class StatusEnum(str, Enum):
    pending = "pending"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"


class OrderResponse(BaseModel):
    id: int = Field(..., gt=0, description="Order ID must be positive")
    user_id: int = Field(..., gt=0, description="User ID must be positive")

    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Name must be 2–100 characters")
    phone: Optional[str] = Field(None, pattern=r"^\+?\d{10,15}$", description="Phone must be 10–15 digits, optional +")
    address: Optional[str] = Field(None, min_length=5, max_length=255, description="Address must be 5–255 characters")

    status: StatusEnum

    items: List[OrderItemResponse] = Field(..., min_items=1, description="Must contain at least one item")


class OrderStatusUpdate(BaseModel):
    status: StatusEnum


class OrderCreate(BaseModel):
    
    name: str = Field(..., min_length=2, max_length=100, description="Name must be 2–100 characters")
    phone: str = Field(..., pattern=r"^\+?\d{10,15}$", description="Phone must be 10–15 digits, optional leading +")
    address: str = Field(..., min_length=5, max_length=255, description="Address must be 5–255 characters")

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value.replace(" ", "").isalpha():
            raise ValueError("Name must contain only letters and spaces")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        value = value.strip()
        digits = value.lstrip("+")
        if not digits.isdigit():
            raise ValueError("Phone must contain only digits, with an optional leading '+'")
        return value

    @field_validator("address")
    @classmethod
    def validate_address(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Address must not be empty or whitespace")
        return value
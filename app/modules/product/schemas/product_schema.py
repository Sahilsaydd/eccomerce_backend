from typing import List

from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name:str =Field(min_length=1 ,max_length=100)
    description:str
    price:float =Field(gt=0)
    category:str =Field(min_length=1 ,max_length=50)

class ProductUpdate(BaseModel):
    name:str =Field(default=None, min_length=1 ,max_length=100)
    description:str =Field(default=None)
    price:float =Field(default=None, gt=0)
    category:str =Field(default=None, min_length=1 ,max_length=50)


class ProductResponse(BaseModel):
    id:int
    name:str
    description:str
    price:float
    category:str
    
    class Config:
        from_attributes = True


class PaginatedProductResponse(BaseModel):
    total_count: int 
    total_pages: int
    current_page: int
    products: List[ProductResponse]
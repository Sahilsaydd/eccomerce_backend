from typing import List, Optional

from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name:str =Field(min_length=1 ,max_length=100)
    description:str
    price:float =Field(gt=0)
    category:str =Field(min_length=1 ,max_length=50)
    product_img:str = Field(default=None) 
    rating:float = Field(default=0.0, ge=0, le=5)  
class ProductUpdate(BaseModel):
    name:str =Field(default=None, min_length=1 ,max_length=100)
    description:str =Field(default=None)
    price:float =Field(default=None, gt=0)
    category:str =Field(default=None, min_length=1 ,max_length=50)
    product_img:str = Field(default=None)  
    rating:float = Field(default=None, ge=0, le=5)  

class ProductResponse(BaseModel):
    id:int
    name:str
    description:str
    price:float
    category:str
    product_img: Optional[str] = None   
    rating: Optional[float] = 0.0
    class Config:
        from_attributes = True


class PaginatedProductResponse(BaseModel):
    total_count: int 
    total_pages: int
    current_page: int
    products: List[ProductResponse]
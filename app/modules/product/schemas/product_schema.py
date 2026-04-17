from pydantic import BaseModel, Field

class ProductCreate(BaseModel):
    name:str =Field(min_length=1 ,max_length=100)
    description:str
    price:float =Field(gt=0)
    category:str =Field(min_length=1 ,max_length=50)

class ProductUpdate(BaseModel):
    name:str | None =None
    description:str | None =None
    price:float | None =None
    category:str | None =None


class ProductResponse(BaseModel):
    id:int
    name:str
    description:str
    price:float
    category:str
    
    class Config:
        from_attributes = True

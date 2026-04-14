from pydantic import BaseModel

class ProductCreate(BaseModel):
    name:str
    description:str
    price:float
    category:str

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

from fastapi import APIRouter ,Depends ,Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.deps.db import get_db
from app.modules.product.schemas.product_schema import ProductCreate ,ProductResponse,ProductUpdate
from app.modules.product.crud import product_crud
from app.deps.auth  import require_role

router = APIRouter(prefix="/products",tags=["Products"])


# search Product

@router.get("/search/")
async def search(keyword:str =Query(None),category:str=Query(None), db:AsyncSession =Depends(get_db)):
    return await product_crud.search_products(db,keyword,category)



# Get By Id 
@router.get("/{product_id}",response_model=ProductResponse)
async def get_one(product_id:int , db:AsyncSession =Depends(get_db)):
    return await product_crud.get_product_by_id(db,product_id)



# Get All (Public)
@router.get("/",response_model=list[ProductResponse])
async def get_all(db:AsyncSession =Depends(get_db)):
    return await product_crud.get_products(db)


# Create (Admin only)
@router.post("/",response_model=ProductResponse)
async def create(data:ProductCreate ,db:AsyncSession =Depends(get_db), user= Depends(require_role(["admin"]))):
    return await product_crud.create_product(db,data)


#update (Admin only)
@router.put("/{product_id}",response_model=ProductResponse)
async def update(product_id:int ,data:ProductUpdate ,db:AsyncSession=Depends(get_db),user=Depends(require_role(["admin"]))):
    return await product_crud.update_product(db,product_id,data)

# Delete All Products (For Testing Only)
@router.delete("/delete_all")
async def delete_all(db:AsyncSession =Depends(get_db),user=Depends(require_role(["admin"]))):
    return await product_crud.delete_all_products(db)


# Delete (only Admin)
@router.delete("/{product_id}")
async def delete(product_id:int, db:AsyncSession =Depends(get_db), user=Depends(require_role(["admin"]))):
    return await product_crud.delete_product(db, product_id)


